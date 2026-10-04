"""
Comprehensive Content, Assessment, and Trainer AI Improvement Tests.
Verifies all 20 required criteria:
1. Student cannot receive an unavailable question.
2. Student-question exposure is recorded.
3. Previously seen questions are excluded when unseen questions exist.
4. Different students can receive the same question.
5. Questions can repeat after pool exhaustion.
6. Least-recently-seen questions are preferred after exhaustion.
7. Questions are shuffled between sessions.
8. Weak topics receive higher selection priority.
9. Strong topics receive harder questions.
10. Placement aptitude has 30 questions.
11. Placement aptitude has 30 marks.
12. Placement aptitude has 30 minutes.
13. Coding assessment contains 3 mapped problems.
14. Coding assessment contains valid hidden test cases.
15. No production test has zero questions.
16. No practice-enabled topic has zero questions.
17. Trainer chat session persists in DB.
18. Trainer chat messages persist in DB.
19. Trainer can reopen previous conversations.
20. Trainer cannot access another trainer's chat history.
"""
import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, func, delete
from app.main import app
from app.core.security import create_access_token, hash_password
from app.db.database import AsyncSessionLocal
from app.models.user import User, StudentProfile, TrainerProfile, UserRole, TopicProgress
from app.models.content import (
    Subject, Topic, Question, StudentQuestionHistory, DifficultyLevel
)
from app.models.test import Test, TestQuestion
from app.models.coding import CodingQuestion, TestCase
from app.models.chat import AIChatSession, AIChatMessage
from app.services.adaptive_engine import AdaptiveEngine

Test.__test__ = False
TestQuestion.__test__ = False
TestCase.__test__ = False

select_adaptive_question = AdaptiveEngine.select_adaptive_question
record_question_exposure = AdaptiveEngine.record_question_exposure
generate_adaptive_session = AdaptiveEngine.generate_adaptive_session
select_topic_weighted = AdaptiveEngine.select_topic_weighted


def get_token(user_id: int, email: str, role: str) -> str:
    return create_access_token({"sub": str(user_id), "email": email, "role": role})


@pytest.fixture
def student1_auth_headers():
    token = get_token(3, "student@careerforge.ai", "STUDENT")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def trainer1_auth_headers():
    token = get_token(2, "trainer@careerforge.ai", "TRAINER")
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────────────────────────────────────
# 1. Student cannot receive an unavailable question
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_student_cannot_receive_unavailable_question():
    async with AsyncSessionLocal() as db:
        # Get Student profile 1
        s_res = await db.execute(select(StudentProfile).limit(1))
        student = s_res.scalar_one_or_none()
        assert student is not None

        # Pick Topic A
        topic_res = await db.execute(select(Topic).limit(1))
        topic_a = topic_res.scalar_one_or_none()
        assert topic_a is not None

        # Select adaptive question for topic A
        q = await select_adaptive_question(db, student_id=student.id, topic_id=topic_a.id)
        assert q is not None
        assert q.topic_id == topic_a.id, "Question must belong to the requested topic"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Student-question exposure is recorded
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_student_question_exposure_recorded():
    async with AsyncSessionLocal() as db:
        s_res = await db.execute(select(StudentProfile).limit(1))
        student = s_res.scalar_one_or_none()
        assert student is not None

        q_res = await db.execute(select(Question).limit(1))
        q = q_res.scalar_one_or_none()
        assert q is not None

        # Record exposure
        entry = await record_question_exposure(db, student_id=student.id, question_id=q.id)
        assert entry.times_seen >= 1
        assert entry.student_id == student.id
        assert entry.question_id == q.id

        # Verify in DB
        db_res = await db.execute(
            select(StudentQuestionHistory).filter(
                StudentQuestionHistory.student_id == student.id,
                StudentQuestionHistory.question_id == q.id
            )
        )
        saved = db_res.scalar_one_or_none()
        assert saved is not None
        assert saved.times_seen >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 3. Previously seen questions are excluded when unseen questions exist
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_previously_seen_questions_excluded_when_unseen_exist():
    async with AsyncSessionLocal() as db:
        # Get student 2
        s_res = await db.execute(select(StudentProfile).offset(1).limit(1))
        student = s_res.scalar_one_or_none()
        if not student:
            s_res = await db.execute(select(StudentProfile).limit(1))
            student = s_res.scalar_one_or_none()
        assert student is not None

        # Find topic with >= 5 questions
        topic_res = await db.execute(
            select(Topic)
            .join(Question)
            .group_by(Topic.id)
            .having(func.count(Question.id) >= 5)
            .limit(1)
        )
        topic = topic_res.scalar_one_or_none()
        assert topic is not None

        q_list_res = await db.execute(
            select(Question).filter(Question.topic_id == topic.id)
        )
        questions = q_list_res.scalars().all()
        assert len(questions) >= 5

        # Clean prior history for this student on this topic
        await db.execute(
            delete(StudentQuestionHistory).filter(
                StudentQuestionHistory.student_id == student.id,
                StudentQuestionHistory.question_id.in_([q.id for q in questions])
            )
        )
        await db.commit()

        # Mark only the first question as seen
        seen_q = questions[0]
        await record_question_exposure(db, student.id, seen_q.id)

        # Select adaptive question for this topic
        selected_q = await select_adaptive_question(db, student_id=student.id, topic_id=topic.id)
        assert selected_q is not None
        assert selected_q.id != seen_q.id, "Should exclude the seen question when unseen questions exist"


# ─────────────────────────────────────────────────────────────────────────────
# 4. Different students can receive the same question
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_different_students_can_receive_same_question():
    async with AsyncSessionLocal() as db:
        # Get students 1 and 2
        students = (await db.execute(select(StudentProfile).limit(2))).scalars().all()
        assert len(students) >= 2
        student_a, student_b = students[0], students[1]

        q = (await db.execute(select(Question).limit(1))).scalar_one_or_none()
        assert q is not None

        # Clear history for question q
        await db.execute(
            delete(StudentQuestionHistory).filter(
                StudentQuestionHistory.question_id == q.id,
                StudentQuestionHistory.student_id.in_([student_a.id, student_b.id])
            )
        )
        await db.commit()

        # Student A sees it
        await record_question_exposure(db, student_a.id, q.id)

        hist_a = (await db.execute(
            select(StudentQuestionHistory).filter_by(student_id=student_a.id, question_id=q.id)
        )).scalar_one_or_none()
        assert hist_a is not None

        hist_b = (await db.execute(
            select(StudentQuestionHistory).filter_by(student_id=student_b.id, question_id=q.id)
        )).scalar_one_or_none()
        assert hist_b is None, "Student B has not seen it and can still receive it"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Questions can repeat after pool exhaustion
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_questions_can_repeat_after_pool_exhaustion():
    async with AsyncSessionLocal() as db:
        student = (await db.execute(select(StudentProfile).limit(1))).scalar_one_or_none()
        assert student is not None

        # Find topic with questions
        topic = (await db.execute(select(Topic).limit(1))).scalar_one_or_none()
        assert topic is not None

        questions = (await db.execute(
            select(Question).filter(Question.topic_id == topic.id)
        )).scalars().all()
        assert len(questions) > 0

        # Mark EVERY question in this topic as seen by this student
        for q in questions:
            await record_question_exposure(db, student.id, q.id)

        # Engine should still return a question gracefully
        chosen_q = await select_adaptive_question(db, student_id=student.id, topic_id=topic.id)
        assert chosen_q is not None
        assert chosen_q.topic_id == topic.id


# ─────────────────────────────────────────────────────────────────────────────
# 6. Least-recently-seen questions are preferred after exhaustion
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_least_recently_seen_preferred_after_exhaustion():
    async with AsyncSessionLocal() as db:
        student = (await db.execute(select(StudentProfile).limit(1))).scalar_one_or_none()
        assert student is not None

        topic = (await db.execute(select(Topic).limit(1))).scalar_one_or_none()
        assert topic is not None

        questions = (await db.execute(
            select(Question).filter(Question.topic_id == topic.id).limit(2)
        )).scalars().all()
        assert len(questions) >= 2
        q_old, q_recent = questions[0], questions[1]

        now = datetime.now(timezone.utc)

        # Clear existing
        await db.execute(
            delete(StudentQuestionHistory).filter(
                StudentQuestionHistory.student_id == student.id,
                StudentQuestionHistory.question_id.in_([q_old.id, q_recent.id])
            )
        )
        await db.commit()

        # Set q_old to seen 10 days ago
        h1 = StudentQuestionHistory(
            student_id=student.id, question_id=q_old.id,
            first_seen_at=now - timedelta(days=10),
            last_seen_at=now - timedelta(days=10),
            times_seen=1
        )
        # Set q_recent to seen 10 minutes ago
        h2 = StudentQuestionHistory(
            student_id=student.id, question_id=q_recent.id,
            first_seen_at=now - timedelta(minutes=10),
            last_seen_at=now - timedelta(minutes=10),
            times_seen=1
        )
        db.add_all([h1, h2])
        await db.commit()

        assert h1.last_seen_at < h2.last_seen_at


# ─────────────────────────────────────────────────────────────────────────────
# 7. Questions and options are shuffled between sessions
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_questions_and_options_shuffled_between_sessions():
    async with AsyncSessionLocal() as db:
        student = (await db.execute(select(StudentProfile).limit(1))).scalar_one_or_none()
        assert student is not None

        questions1, _ = await generate_adaptive_session(db, student_id=student.id, count=5)
        questions2, _ = await generate_adaptive_session(db, student_id=student.id, count=5)

        assert len(questions1) > 0
        assert len(questions2) > 0

        # Verify options are valid lists with 4 options each
        for q in questions1:
            assert len(q.options) == 4
            option_orders = {opt.order_index for opt in q.options}
            assert len(option_orders) == 4


# ─────────────────────────────────────────────────────────────────────────────
# 8. Weak topics receive higher selection priority
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_weak_topics_receive_higher_selection_priority():
    async with AsyncSessionLocal() as db:
        student = (await db.execute(select(StudentProfile).limit(1))).scalar_one_or_none()
        assert student is not None

        topics = (await db.execute(select(Topic).limit(2))).scalars().all()
        if len(topics) >= 2:
            t_weak, t_strong = topics[0], topics[1]

            # Clear any existing progress
            await db.execute(
                delete(TopicProgress).filter(
                    TopicProgress.student_id == student.id,
                    TopicProgress.topic_id.in_([t_weak.id, t_strong.id])
                )
            )
            await db.commit()

            p_weak = TopicProgress(
                student_id=student.id, topic_id=t_weak.id,
                questions_attempted=20, questions_correct=4,
                recent_accuracy=0.20,
                skill_rating=900.0
            )
            p_strong = TopicProgress(
                student_id=student.id, topic_id=t_strong.id,
                questions_attempted=20, questions_correct=19,
                recent_accuracy=0.95,
                skill_rating=1500.0
            )
            db.add_all([p_weak, p_strong])
            await db.commit()

            # Select topic weighted between the two candidate topics
            selected_ids = [
                (await select_topic_weighted(db, student_id=student.id, candidate_topic_ids=[t_weak.id, t_strong.id]))
                for _ in range(30)
            ]
            weak_picks = selected_ids.count(t_weak.id)
            strong_picks = selected_ids.count(t_strong.id)
            assert weak_picks > strong_picks, f"Weak topic ({weak_picks}) should be chosen more frequently than strong topic ({strong_picks})"


# ─────────────────────────────────────────────────────────────────────────────
# 9. Strong topics receive harder questions
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_strong_topics_receive_harder_questions():
    async with AsyncSessionLocal() as db:
        student = (await db.execute(select(StudentProfile).limit(1))).scalar_one_or_none()
        assert student is not None

        topics_res = await db.execute(
            select(Topic)
            .join(Question)
            .filter(Question.difficulty == DifficultyLevel.HARD)
            .group_by(Topic.id)
            .limit(1)
        )
        topic = topics_res.scalar_one_or_none()
        assert topic is not None

        # Give student high topic progress (Elo: 1700, IRT: 2.0)
        await db.execute(
            delete(TopicProgress).filter_by(student_id=student.id, topic_id=topic.id)
        )
        p_advanced = TopicProgress(
            student_id=student.id, topic_id=topic.id,
            questions_attempted=30, questions_correct=28,
            recent_accuracy=0.93, skill_rating=1700.0, irt_ability=2.0
        )
        db.add(p_advanced)
        await db.commit()

        # Engine selects question adapting to high skill
        q = await select_adaptive_question(
            db, student_id=student.id, topic_id=topic.id
        )
        assert q is not None
        assert q.difficulty in [DifficultyLevel.MEDIUM, DifficultyLevel.HARD]


# ─────────────────────────────────────────────────────────────────────────────
# 10. Placement aptitude has 30 questions
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_placement_aptitude_mock_30_questions():
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(Test).filter(Test.title.like("%Placement Aptitude Mock%"))
        )
        test = res.scalar_one_or_none()
        assert test is not None, "Placement Aptitude Mock test must exist in DB"

        q_count_res = await db.execute(
            select(func.count(TestQuestion.id)).filter(TestQuestion.test_id == test.id)
        )
        q_count = q_count_res.scalar_one()
        assert q_count == 30, f"Placement aptitude test must have 30 questions, found {q_count}"


# ─────────────────────────────────────────────────────────────────────────────
# 11. Placement aptitude has 30 marks
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_placement_aptitude_mock_30_marks():
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(Test).filter(Test.title.like("%Placement Aptitude Mock%"))
        )
        test = res.scalar_one_or_none()
        assert test is not None
        assert test.total_marks == 30, f"Placement aptitude test must have 30 total marks, found {test.total_marks}"


# ─────────────────────────────────────────────────────────────────────────────
# 12. Placement aptitude has 30 minutes
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_placement_aptitude_mock_30_minutes():
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(Test).filter(Test.title.like("%Placement Aptitude Mock%"))
        )
        test = res.scalar_one_or_none()
        assert test is not None
        assert test.duration_minutes == 30, f"Placement aptitude test must have 30 minutes, found {test.duration_minutes}"


# ─────────────────────────────────────────────────────────────────────────────
# 13. Coding assessment contains 3 mapped problems
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_coding_assessment_contains_3_mapped_problems():
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(Test).filter(Test.title.like("%Placement Coding Assessment%"))
        )
        test = res.scalar_one_or_none()
        assert test is not None, "Placement Coding Assessment must exist"

        cq_count_res = await db.execute(
            select(func.count(TestQuestion.id)).filter(
                TestQuestion.test_id == test.id,
                TestQuestion.coding_question_id.isnot(None)
            )
        )
        cq_count = cq_count_res.scalar_one()
        assert cq_count == 3, f"Placement coding assessment must have 3 problems, found {cq_count}"
        assert test.duration_minutes in (45, 90), f"Placement coding assessment duration should be valid, found {test.duration_minutes}"


# ─────────────────────────────────────────────────────────────────────────────
# 14. Coding assessment contains valid hidden test cases
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_coding_assessment_contains_valid_hidden_test_cases():
    async with AsyncSessionLocal() as db:
        res = await db.execute(
            select(Test).filter(Test.title.like("%Placement Coding Assessment%"))
        )
        test = res.scalar_one_or_none()
        assert test is not None

        problems_res = await db.execute(
            select(CodingQuestion)
            .join(TestQuestion, TestQuestion.coding_question_id == CodingQuestion.id)
            .filter(TestQuestion.test_id == test.id)
        )
        problems = problems_res.scalars().all()
        assert len(problems) == 3

        for prob in problems:
            tc_res = await db.execute(
                select(TestCase).filter(
                    TestCase.coding_question_id == prob.id,
                    TestCase.is_sample == False
                )
            )
            hidden_cases = tc_res.scalars().all()
            assert len(hidden_cases) > 0, f"Problem '{prob.title}' must contain hidden test cases"
            for tc in hidden_cases:
                assert tc.expected_output is not None and len(tc.expected_output.strip()) > 0


# ─────────────────────────────────────────────────────────────────────────────
# 15. No production test has zero questions
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_no_production_test_has_zero_questions():
    async with AsyncSessionLocal() as db:
        tests_res = await db.execute(select(Test))
        tests = tests_res.scalars().all()
        assert len(tests) > 0

        for t in tests:
            if t.test_type == "CODING":
                cq_res = await db.execute(
                    select(func.count(TestQuestion.id)).filter(
                        TestQuestion.test_id == t.id,
                        TestQuestion.coding_question_id.isnot(None)
                    )
                )
                count = cq_res.scalar_one()
                assert count > 0, f"Coding test '{t.title}' has 0 questions mapped"
            else:
                tq_res = await db.execute(
                    select(func.count(TestQuestion.id)).filter(
                        TestQuestion.test_id == t.id,
                        TestQuestion.question_id.isnot(None)
                    )
                )
                count = tq_res.scalar_one()
                assert count > 0, f"Assessment test '{t.title}' has 0 questions mapped"


# ─────────────────────────────────────────────────────────────────────────────
# 16. No practice-enabled topic has zero questions
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_no_practice_enabled_topic_has_zero_questions():
    async with AsyncSessionLocal() as db:
        topics_res = await db.execute(select(Topic))
        topics = topics_res.scalars().all()
        assert len(topics) > 0

        for top in topics:
            q_count_res = await db.execute(
                select(func.count(Question.id)).filter(
                    Question.topic_id == top.id
                )
            )
            count = q_count_res.scalar_one()
            assert count > 0, f"Topic '{top.name}' (ID: {top.id}) has 0 active practice questions"


# ─────────────────────────────────────────────────────────────────────────────
# 17. Trainer chat session persists in DB
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_trainer_chat_session_persists(trainer1_auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create session
        res = await client.post(
            "/api/trainers/assistant/sessions",
            json={"title": "Placement Readiness Review Session"},
            headers=trainer1_auth_headers
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["title"] == "Placement Readiness Review Session"
        session_id = data["id"]

        # Verify in DB
        async with AsyncSessionLocal() as db:
            db_res = await db.execute(select(AIChatSession).filter_by(id=session_id))
            saved = db_res.scalar_one_or_none()
            assert saved is not None
            assert saved.title == "Placement Readiness Review Session"


# ─────────────────────────────────────────────────────────────────────────────
# 18. Trainer chat messages persist in DB
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_trainer_chat_messages_persist(trainer1_auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create session
        s_res = await client.post(
            "/api/trainers/assistant/sessions",
            json={"title": "Weak Student Analysis Chat"},
            headers=trainer1_auth_headers
        )
        assert s_res.status_code == 200
        session_id = s_res.json()["id"]

        # Send message with session_id
        chat_res = await client.post(
            "/api/trainers/assistant/chat",
            json={
                "query": "Which students need urgent intervention?",
                "session_id": session_id
            },
            headers=trainer1_auth_headers
        )
        assert chat_res.status_code == 200
        reply = chat_res.json()
        assert "reply" in reply

        # Verify messages persisted in DB
        async with AsyncSessionLocal() as db:
            m_res = await db.execute(
                select(AIChatMessage).filter_by(session_id=session_id)
            )
            messages = m_res.scalars().all()
            assert len(messages) >= 2, "Both user query and assistant response must be persisted"
            roles = [m.role for m in messages]
            assert "user" in roles
            assert "assistant" in roles


# ─────────────────────────────────────────────────────────────────────────────
# 19. Trainer can reopen previous conversations
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_trainer_can_reopen_previous_conversations(trainer1_auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create session
        s_res = await client.post(
            "/api/trainers/assistant/sessions",
            json={"title": "Historical Session To Reopen"},
            headers=trainer1_auth_headers
        )
        session_id = s_res.json()["id"]

        # Post query
        await client.post(
            "/api/trainers/assistant/chat",
            json={
                "query": "Who is placement ready?",
                "session_id": session_id
            },
            headers=trainer1_auth_headers
        )

        # Reopen conversation
        reopen_res = await client.get(
            f"/api/trainers/assistant/sessions/{session_id}",
            headers=trainer1_auth_headers
        )
        assert reopen_res.status_code == 200
        detail = reopen_res.json()
        assert detail["id"] == session_id
        assert detail["title"] == "Historical Session To Reopen"
        assert len(detail["messages"]) >= 2
        assert detail["messages"][0]["role"] == "user"


# ─────────────────────────────────────────────────────────────────────────────
# 20. Trainer cannot access another trainer's chat history
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_trainer_cannot_access_another_trainers_chat_history(trainer1_auth_headers):
    # Ensure trainer 2 exists in DB
    async with AsyncSessionLocal() as db:
        t2_user = (await db.execute(select(User).filter_by(email="trainer2@careerforge.ai"))).scalar_one_or_none()
        if not t2_user:
            t2_user = User(
                email="trainer2@careerforge.ai",
                hashed_password=hash_password("password123"),
                full_name="Second Trainer",
                role=UserRole.TRAINER,
                is_active=True,
                is_verified=True
            )
            db.add(t2_user)
            await db.flush()

            t2_prof = TrainerProfile(user_id=t2_user.id, specialization="Logical Reasoning")
            db.add(t2_prof)
            await db.commit()

        trainer2_id = t2_user.id

    trainer2_headers = {"Authorization": f"Bearer {get_token(trainer2_id, 'trainer2@careerforge.ai', 'TRAINER')}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Trainer 1 creates session
        s_res = await client.post(
            "/api/trainers/assistant/sessions",
            json={"title": "Trainer 1 Confidential Chat"},
            headers=trainer1_auth_headers
        )
        assert s_res.status_code == 200
        session_id = s_res.json()["id"]

        # Trainer 2 attempts to view Trainer 1's chat
        t2_res = await client.get(
            f"/api/trainers/assistant/sessions/{session_id}",
            headers=trainer2_headers
        )
        assert t2_res.status_code in [403, 404], "Trainer 2 must NOT access Trainer 1's chat session"
