"""
Comprehensive Automated Tests for Personalized Adaptive Aptitude Engine.
Verifies:
1. Weak topic receives higher selection priority.
2. Strong topic receives harder questions.
3. Difficulty changes dynamically according to performance (ZPD adaptation).
4. Previously answered questions are not repeatedly selected unnecessarily.
5. New students without enough data receive a balanced/default exploration distribution.
6. The system continuously updates student topic skill rating (Elo & IRT theta) after answers.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.adaptive_engine import AdaptiveEngine, DIFFICULTY_TO_IRT
from app.models.content import Topic, Question, PracticeAttempt, DifficultyLevel
from app.models.user import StudentProfile, TopicProgress, User
from app.db.database import AsyncSessionLocal
from sqlalchemy import select, delete


@pytest.mark.asyncio
async def test_continuous_skill_update_after_answers():
    """System continuously updates the student's topic skill (Elo & IRT theta) after answers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login student
        login_res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "Student@1234",
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Fetch questions for Percentages topic (topic_id=2 typically)
        async with AsyncSessionLocal() as db:
            p_topic = (await db.execute(select(Topic).where(Topic.name == "Percentages"))).scalar_one()
            q_res = await db.execute(
                select(Question).where(Question.topic_id == p_topic.id)
            )
            question = q_res.scalars().first()
            assert question is not None

            # Get initial skill
            prog = (await db.execute(
                select(TopicProgress)
                .where(TopicProgress.student_id == 1)
                .where(TopicProgress.topic_id == p_topic.id)
            )).scalar_one_or_none()
            initial_skill = prog.skill_rating if prog else 1000.0

        # Submit correct answer
        async with AsyncSessionLocal() as db:
            q_full = (await db.execute(
                select(Question).where(Question.id == question.id)
            )).scalar_one()
            from sqlalchemy.orm import selectinload
            opt_res = await db.execute(
                select(Question).where(Question.id == question.id).options(selectinload(Question.options))
            )
            correct_opt = next(o for o in opt_res.scalar_one().options if o.is_correct)

        submit_res = await client.post("/api/students/practice/submit", json={
            "question_id": question.id,
            "selected_option_id": correct_opt.id,
            "time_taken_seconds": 12,
        }, headers=headers)
        assert submit_res.status_code == 200, submit_res.text
        data = submit_res.json()

        assert data["is_correct"] is True
        assert data["new_skill_rating"] > data["old_skill_rating"]
        assert data["skill_delta"] > 0
        assert "adaptive_message" in data


@pytest.mark.asyncio
async def test_weak_topic_higher_selection_priority():
    """A weak topic (low accuracy) receives significantly higher selection priority than a mastered topic."""
    async with AsyncSessionLocal() as db:
        # Create student profile simulation with weak topic vs strong topic
        # Topic 1: Percentages (Strong: 90% accuracy, skill 1250)
        # Topic 2: Syllogisms (Weak: 30% accuracy, skill 780)
        perc_t = (await db.execute(select(Topic).where(Topic.name == "Percentages"))).scalar_one()
        syl_t = (await db.execute(select(Topic).where(Topic.name == "Syllogisms"))).scalar_one()

        # Set up progress records for student 1
        prog_perc = (await db.execute(
            select(TopicProgress).where(TopicProgress.student_id == 1).where(TopicProgress.topic_id == perc_t.id)
        )).scalar_one_or_none()
        if not prog_perc:
            prog_perc = TopicProgress(student_id=1, topic_id=perc_t.id)
            db.add(prog_perc)
        prog_perc.questions_attempted = 10
        prog_perc.questions_correct = 9  # 90% accuracy
        prog_perc.skill_rating = 1250.0
        prog_perc.recent_accuracy = 0.9

        prog_syl = (await db.execute(
            select(TopicProgress).where(TopicProgress.student_id == 1).where(TopicProgress.topic_id == syl_t.id)
        )).scalar_one_or_none()
        if not prog_syl:
            prog_syl = TopicProgress(student_id=1, topic_id=syl_t.id)
            db.add(prog_syl)
        prog_syl.questions_attempted = 10
        prog_syl.questions_correct = 3  # 30% accuracy (Weak)
        prog_syl.skill_rating = 780.0
        prog_syl.recent_accuracy = 0.3

        await db.commit()

        # Perform 100 topic selection simulations restricted to these two topics
        counts = {perc_t.id: 0, syl_t.id: 0}
        for _ in range(100):
            chosen = await AdaptiveEngine.select_topic_weighted(
                db, student_id=1, candidate_topic_ids=[perc_t.id, syl_t.id]
            )
            counts[chosen] += 1

        # Weak topic (Syllogisms) must be selected significantly more often than strong topic (Percentages)
        assert counts[syl_t.id] > counts[perc_t.id] * 2, (
            f"Expected weak topic {syl_t.id} to have >2x selections vs strong {perc_t.id}. Got {counts}"
        )


@pytest.mark.asyncio
async def test_strong_topic_receives_harder_questions():
    """A strong topic (high accuracy & high streak/theta) selects HARD questions."""
    async with AsyncSessionLocal() as db:
        perc_t = (await db.execute(select(Topic).where(Topic.name == "Percentages"))).scalar_one()

        prog_perc = (await db.execute(
            select(TopicProgress).where(TopicProgress.student_id == 1).where(TopicProgress.topic_id == perc_t.id)
        )).scalar_one()
        prog_perc.questions_attempted = 15
        prog_perc.questions_correct = 14
        prog_perc.streak = 4
        prog_perc.irt_ability = 1.2
        prog_perc.skill_rating = 1350.0
        await db.commit()

        # Select question for Percentages topic
        selected_q = await AdaptiveEngine.select_adaptive_question(
            db, student_id=1, topic_id=perc_t.id
        )
        assert selected_q is not None
        assert selected_q.difficulty == DifficultyLevel.HARD, (
            f"Expected HARD question for master student, got {selected_q.difficulty}"
        )


@pytest.mark.asyncio
async def test_weak_student_receives_easy_questions_to_rebuild():
    """A weak topic with low accuracy receives EASY foundational questions to rebuild skill."""
    async with AsyncSessionLocal() as db:
        syl_t = (await db.execute(select(Topic).where(Topic.name == "Syllogisms"))).scalar_one()

        prog_syl = (await db.execute(
            select(TopicProgress).where(TopicProgress.student_id == 1).where(TopicProgress.topic_id == syl_t.id)
        )).scalar_one()
        prog_syl.questions_attempted = 10
        prog_syl.questions_correct = 2  # 20% accuracy
        prog_syl.streak = 0
        prog_syl.irt_ability = -1.2
        prog_syl.skill_rating = 700.0
        await db.commit()

        # Select question for Syllogisms
        selected_q = await AdaptiveEngine.select_adaptive_question(
            db, student_id=1, topic_id=syl_t.id
        )
        assert selected_q is not None
        assert selected_q.difficulty == DifficultyLevel.EASY, (
            f"Expected EASY foundational question for struggling student, got {selected_q.difficulty}"
        )


@pytest.mark.asyncio
async def test_difficulty_changes_according_to_performance():
    """Difficulty dynamically shifts from EASY -> MEDIUM -> HARD as answers are correct."""
    # Test deterministic difficulty mapping function
    assert AdaptiveEngine.difficulty_for_ability(theta=-1.0, accuracy=0.3, streak=0) == DifficultyLevel.EASY
    assert AdaptiveEngine.difficulty_for_ability(theta=0.1, accuracy=0.65, streak=1) == DifficultyLevel.MEDIUM
    assert AdaptiveEngine.difficulty_for_ability(theta=1.0, accuracy=0.85, streak=3) == DifficultyLevel.HARD


@pytest.mark.asyncio
async def test_previously_answered_questions_not_repeated_unnecessarily():
    """Previously answered questions are excluded when unattempted questions are available in the bank."""
    async with AsyncSessionLocal() as db:
        p_topic = (await db.execute(select(Topic).where(Topic.name == "Profit & Loss"))).scalar_one()
        all_q = (await db.execute(select(Question).where(Question.topic_id == p_topic.id))).scalars().all()
        assert len(all_q) >= 2

        # Mark question 1 as already attempted
        q1 = all_q[0]
        q2 = all_q[1]

        # Clean previous attempts for student 2 (alice)
        await db.execute(
            delete(PracticeAttempt)
            .where(PracticeAttempt.student_id == 2)
            .where(PracticeAttempt.question_id.in_([q.id for q in all_q]))
        )
        db.add(PracticeAttempt(
            student_id=2,
            question_id=q1.id,
            selected_option_id=None,
            is_correct=True,
            time_taken_seconds=10,
        ))
        await db.commit()

        # When student 2 requests next question, q1 should not be selected if other questions exist
        selected = await AdaptiveEngine.select_adaptive_question(
            db, student_id=2, topic_id=p_topic.id
        )
        assert selected is not None
        assert selected.id != q1.id, f"Expected unattempted question, but got already attempted question {q1.id}"


@pytest.mark.asyncio
async def test_new_students_receive_exploration_distribution():
    """New students with zero/insufficient data receive exploration weight across topics."""
    async with AsyncSessionLocal() as db:
        # Create a fresh test student profile without any topic history
        analytics = await AdaptiveEngine.get_student_topic_analytics(db, student_id=99999)
        assert len(analytics) > 0

        # All topics should be classified as EXPLORING
        for a in analytics:
            assert a["category"] == "EXPLORING"
            assert a["questions_attempted"] == 0

        # Select a topic: must successfully select without error
        selected_tid = await AdaptiveEngine.select_topic_weighted(db, student_id=99999)
        assert selected_tid is not None


@pytest.mark.asyncio
async def test_personalization_insights_api():
    """Personalization insights endpoint returns diagnostic tips and recommendation banner."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "Student@1234",
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = await client.get("/api/students/adaptive/insights", headers=headers)
        assert res.status_code == 200, res.text
        data = res.json()
        assert "recommendation_banner" in data
        assert "recommended_topic_id" in data
        assert "tips" in data
        assert "topic_analytics" in data
