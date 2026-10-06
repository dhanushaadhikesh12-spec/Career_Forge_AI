"""
Student routes: dashboard, profile, learning hub, practice, test.
"""
from datetime import datetime, timezone
from typing import List, Optional
import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.api.deps import get_student_profile, get_current_user
from app.models.user import StudentProfile, TopicProgress, User
from app.models.content import (
    Subject, Topic, Lesson, LessonCompletion, Question,
    QuestionOption, PracticeAttempt, DifficultyLevel, StudentQuestionHistory
)
from app.models.test import Test, TestAttempt, TestAnswer, TestQuestion, AttemptStatus, TestStatus, TestType
from app.models.coding import CodingQuestion, CodeSubmission, SubmissionVerdict
from app.schemas.content import (
    SubjectOut, TopicOut, LessonOut, QuestionOut, QuestionOptionOut,
    PracticeSessionRequest, PracticeAnswerSubmit, PracticeAnswerResult,
    TopicProgressOut, QuestionOptionWithAnswer, QuestionWithAnswer,
)
from app.schemas.test import (
    TestOut, TestStartResponse, TestSubmitRequest, TestAttemptResult, TestAttemptOut,
)
from app.services.scoring import calculate_and_sync_student_scores
import logging

router = APIRouter(prefix="/students", tags=["Student"])
logger = logging.getLogger(__name__)


# ─────────────────────────────── Dashboard ────────────────────────────────

@router.get("/dashboard")
async def student_dashboard(
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    # Recent attempts
    result = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.student_id == profile.id)
        .where(TestAttempt.status == AttemptStatus.GRADED)
        .order_by(TestAttempt.submitted_at.desc().nullslast(), TestAttempt.id.desc())
        .limit(5)
        .options(selectinload(TestAttempt.test))
    )
    recent_attempts = result.scalars().all()

    # Calculate and synchronize dynamic, authoritative scores and topic progress
    metrics = await calculate_and_sync_student_scores(db, profile)

    # Topic progress (freshly synchronized with actual practice attempts and test answers)
    tp_result = await db.execute(
        select(TopicProgress)
        .where(TopicProgress.student_id == profile.id)
        .options(selectinload(TopicProgress.topic))
    )
    topic_progresses = tp_result.scalars().all()

    # Calculate weak topics (accuracy < 50% with at least 1 attempted question)
    weak_topics = []
    for tp in topic_progresses:
        if tp.questions_attempted >= 1:
            acc = (tp.questions_correct / tp.questions_attempted) * 100.0
            if acc < 50.0:
                weak_topics.append({
                    "topic_id": tp.topic_id,
                    "topic_name": tp.topic.name if tp.topic else "Unknown",
                    "accuracy": round(acc, 1),
                    "skill_rating": round(tp.skill_rating, 1),
                    "questions_attempted": tp.questions_attempted,
                    "questions_correct": tp.questions_correct,
                    "category_label": "Needs Urgent Practice" if acc < 40.0 else "Needs Practice",
                })

    # Sort strictly by lowest accuracy first, tie-breaking by higher attempted count
    weak_topics.sort(key=lambda x: (x["accuracy"], -x["questions_attempted"]))

    return {
        "student": {
            "id": profile.id,
            "full_name": profile.user.full_name if hasattr(profile, "user") else "",
            "total_score": metrics["total_score"],
            "aptitude_score": metrics["aptitude_score"],
            "coding_score": metrics["coding_score"],
            "streak_days": profile.streak_days,
        },
        "recent_tests": [
            {
                "attempt_id": a.id,
                "test_title": a.test.title if a.test else "",
                "score": a.score,
                "percentage": a.percentage,
                "submitted_at": a.submitted_at,
            }
            for a in recent_attempts
        ],
        "weak_topics": weak_topics[:5],
        "practice_count": metrics["practice_count"],
        "tests_taken": metrics["tests_taken"],
        "topic_progress_count": len(topic_progresses),
    }


@router.get("/profile", response_model=dict)
async def get_profile(
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    # Load user relationship
    result = await db.execute(
        select(StudentProfile)
        .where(StudentProfile.id == profile.id)
        .options(selectinload(StudentProfile.user))
    )
    full_profile = result.scalar_one_or_none()
    return {
        "id": full_profile.id,
        "email": full_profile.user.email,
        "full_name": full_profile.user.full_name,
        "college": full_profile.college,
        "department": full_profile.department,
        "graduation_year": full_profile.graduation_year,
        "phone": full_profile.phone,
        "bio": full_profile.bio,
        "total_score": full_profile.total_score,
        "aptitude_score": full_profile.aptitude_score,
        "coding_score": full_profile.coding_score,
        "streak_days": full_profile.streak_days,
    }


# ─────────────────────────────── Learning Hub ────────────────────────────────

@router.get("/subjects", response_model=List[SubjectOut])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject).order_by(Subject.order_index))
    return result.scalars().all()


@router.get("/subjects/{subject_id}/topics", response_model=List[TopicOut])
async def list_topics(subject_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Topic).where(Topic.subject_id == subject_id).order_by(Topic.order_index)
    )
    topics = result.scalars().all()
    out = []
    for t in topics:
        lesson_count = await db.execute(
            select(func.count(Lesson.id)).where(Lesson.topic_id == t.id)
        )
        q_count = await db.execute(
            select(func.count(Question.id)).where(Question.topic_id == t.id)
        )
        out.append(TopicOut(
            id=t.id,
            subject_id=t.subject_id,
            name=t.name,
            description=t.description,
            order_index=t.order_index,
            total_lessons=lesson_count.scalar() or 0,
            total_questions=q_count.scalar() or 0,
        ))
    return out


@router.get("/topics/{topic_id}/lessons", response_model=List[LessonOut])
async def list_lessons(topic_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lesson).where(Lesson.topic_id == topic_id).order_by(Lesson.order_index)
    )
    return result.scalars().all()


@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: int,
    time_spent_seconds: int = 0,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    # Check lesson exists
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Idempotent: check if already completed
    existing = await db.execute(
        select(LessonCompletion)
        .where(LessonCompletion.lesson_id == lesson_id)
        .where(LessonCompletion.student_id == profile.id)
    )
    if not existing.scalar_one_or_none():
        db.add(LessonCompletion(
            lesson_id=lesson_id,
            student_id=profile.id,
            time_spent_seconds=time_spent_seconds,
        ))
        # Update topic progress
        tp = await _get_or_create_topic_progress(db, profile.id, lesson.topic_id)
        tp.lessons_completed = min(tp.lessons_completed + 1, tp.total_lessons or 999)
        await db.commit()

    return {"message": "Lesson marked complete"}


# ─────────────────────────────── Adaptive Aptitude Engine ────────────────────────────────

@router.get("/adaptive/insights")
async def get_adaptive_insights(
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    from app.services.adaptive_engine import AdaptiveEngine
    return await AdaptiveEngine.get_personalization_insights(db, profile.id)


@router.post("/adaptive/session")
async def generate_adaptive_session(
    payload: dict = {},
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    from app.services.adaptive_engine import AdaptiveEngine
    topic_id = payload.get("topic_id")
    count = payload.get("count", 5)

    questions, insights = await AdaptiveEngine.generate_adaptive_session(
        db=db,
        student_id=profile.id,
        topic_id=topic_id,
        count=count,
    )

    return {
        "insights": insights,
        "questions": [
            QuestionOut(
                id=q.id,
                topic_id=q.topic_id,
                text=q.text,
                question_type=q.question_type,
                difficulty=q.difficulty,
                explanation=None,
                points=q.points,
                options=[QuestionOptionOut(id=o.id, text=o.text, order_index=o.order_index) for o in q.options],
            )
            for q in questions
        ],
    }


# ─────────────────────────────── Practice ────────────────────────────────

@router.post("/practice/session", response_model=List[QuestionOut])
async def start_practice(
    payload: PracticeSessionRequest,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    from app.services.adaptive_engine import AdaptiveEngine

    topic_id = payload.topic_id
    if topic_id is None:
        topic_id = await AdaptiveEngine.select_topic_weighted(db, profile.id)

    if payload.difficulty:
        query = select(Question).where(Question.topic_id == topic_id).where(Question.difficulty == payload.difficulty)
        result = await db.execute(query.options(selectinload(Question.options)))
        questions = result.scalars().all()
        if not questions:
            # Fallback to any difficulty in topic
            query = select(Question).where(Question.topic_id == topic_id)
            result = await db.execute(query.options(selectinload(Question.options)))
            questions = result.scalars().all()
        if not questions:
            raise HTTPException(status_code=404, detail="No questions found for this topic")
        
        # Check student history to prioritize unseen questions
        hist_res = await db.execute(
            select(StudentQuestionHistory)
            .where(StudentQuestionHistory.student_id == profile.id)
        )
        history_map = {h.question_id: h for h in hist_res.scalars().all()}
        unseen = [q for q in questions if q.id not in history_map]

        if len(unseen) >= payload.count:
            selected = random.sample(unseen, payload.count)
        else:
            # Need to fill remainder from seen questions, prioritizing least recently seen
            seen = [q for q in questions if q.id in history_map]
            seen.sort(key=lambda q: (history_map[q.id].last_seen_at or datetime.min.replace(tzinfo=timezone.utc)))
            selected = list(unseen) + seen[:(payload.count - len(unseen))]
            random.shuffle(selected)

        # Batch record exposure in strictly ascending ID order
        for q in sorted(selected, key=lambda x: x.id):
            try:
                await AdaptiveEngine.record_question_exposure(db, profile.id, q.id)
            except Exception as e:
                logger.warning(f"Error recording question exposure: {e}")
    else:
        # Use Personalized Adaptive Engine to choose optimal questions
        selected, _ = await AdaptiveEngine.generate_adaptive_session(
            db=db,
            student_id=profile.id,
            topic_id=topic_id,
            count=payload.count,
        )
        if not selected:
            # Fallback to any questions in topic
            query = select(Question).where(Question.topic_id == topic_id)
            result = await db.execute(query.options(selectinload(Question.options)))
            all_q = result.scalars().all()
            if not all_q:
                # Global fallback to any available questions
                query = select(Question).limit(payload.count)
                result = await db.execute(query.options(selectinload(Question.options)))
                all_q = result.scalars().all()
            if not all_q:
                raise HTTPException(status_code=404, detail="No questions found")
            selected = random.sample(all_q, min(payload.count, len(all_q)))
            for q in sorted(selected, key=lambda x: x.id):
                try:
                    await AdaptiveEngine.record_question_exposure(db, profile.id, q.id)
                except Exception as e:
                    logger.warning(f"Error recording question exposure: {e}")

    await db.commit()

    out = []
    for q in selected:
        opts = list(q.options)
        random.shuffle(opts)
        out.append(
            QuestionOut(
                id=q.id,
                topic_id=q.topic_id,
                text=q.text,
                question_type=q.question_type,
                difficulty=q.difficulty,
                explanation=None,  # Hide explanation before attempt
                points=q.points,
                options=[QuestionOptionOut(id=o.id, text=o.text, order_index=idx) for idx, o in enumerate(opts)],
            )
        )
    return out



@router.post("/practice/submit", response_model=PracticeAnswerResult)
async def submit_practice_answer(
    payload: PracticeAnswerSubmit,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    from app.services.adaptive_engine import AdaptiveEngine

    try:
        res = await AdaptiveEngine.record_attempt_and_update_state(
            db=db,
            student_id=profile.id,
            question_id=payload.question_id,
            selected_option_id=payload.selected_option_id,
            time_taken_seconds=payload.time_taken_seconds,
        )
        return PracticeAnswerResult(**res)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────────── Tests ────────────────────────────────

@router.get("/tests", response_model=List[TestOut])
async def list_available_tests(
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    # Tests available to this student's batch(es) or open tests
    result = await db.execute(
        select(Test)
        .where(Test.status == TestStatus.PUBLISHED)
        .order_by(Test.created_at.desc())
    )
    tests = result.scalars().all()

    out = []
    for t in tests:
        if t.test_type == TestType.CODING:
            q_cnt = 20
        else:
            q_count = await db.execute(
                select(func.count(TestQuestion.id)).where(TestQuestion.test_id == t.id)
            )
            q_cnt = q_count.scalar() or 30

        out.append(TestOut(
            id=t.id,
            title=t.title,
            description=t.description,
            test_type=t.test_type,
            status=t.status,
            batch_id=t.batch_id,
            duration_minutes=t.duration_minutes,
            total_marks=t.total_marks,
            passing_marks=t.passing_marks,
            instructions=t.instructions,
            randomize_questions=t.randomize_questions,
            show_results_immediately=t.show_results_immediately,
            scheduled_at=t.scheduled_at,
            created_at=t.created_at,
            question_count=q_cnt,
        ))
    return out


@router.post("/tests/{test_id}/start", response_model=TestStartResponse)
async def start_test(
    test_id: int,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Test).where(Test.id == test_id).options(
            selectinload(Test.test_questions).selectinload(TestQuestion.question).selectinload(Question.options)
        )
    )
    test = result.scalar_one_or_none()
    if not test or test.status != TestStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Test not found or not available")

    # Check for active attempt
    existing = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.test_id == test_id)
        .where(TestAttempt.student_id == profile.id)
        .where(TestAttempt.status == AttemptStatus.IN_PROGRESS)
        .order_by(TestAttempt.id.desc())
    )
    active_attempt = existing.scalars().first()
    now = datetime.now(timezone.utc)

    # If active attempt exists but has expired, mark it timed out so student can start fresh
    if active_attempt and active_attempt.expires_at:
        exp = active_attempt.expires_at if active_attempt.expires_at.tzinfo else active_attempt.expires_at.replace(tzinfo=timezone.utc)
        if now > exp:
            active_attempt.status = AttemptStatus.TIMED_OUT
            active_attempt.submitted_at = exp
            await db.commit()
            active_attempt = None

    if active_attempt:
        # Resume existing: preserve exact same test attempt and question set on refresh
        attempt = active_attempt
        if not attempt.question_order:
            mcq_questions = [tq for tq in test.test_questions if tq.question_id]
            attempt.question_order = [tq.question_id for tq in mcq_questions]
            await db.commit()
    else:
        from datetime import timedelta
        expires_at = now + timedelta(minutes=test.duration_minutes)
        attempt = TestAttempt(
            test_id=test_id,
            student_id=profile.id,
            status=AttemptStatus.IN_PROGRESS,
            expires_at=expires_at,
            max_score=float(test.total_marks or 30),
        )
        db.add(attempt)
        await db.flush()

        # Dynamic selection from large question bank (preventing repetition)
        # Collect previously seen question IDs for this student in past tests
        seen_test_qids = set()
        past_ans_res = await db.execute(
            select(TestAnswer.question_id)
            .join(TestAttempt, TestAttempt.id == TestAnswer.attempt_id)
            .where(TestAttempt.student_id == profile.id)
        )
        for r in past_ans_res.scalars().all():
            if r:
                seen_test_qids.add(r)

        past_order_res = await db.execute(
            select(TestAttempt.question_order)
            .where(TestAttempt.student_id == profile.id)
        )
        for row in past_order_res.scalars().all():
            if row and isinstance(row, list):
                for qid in row:
                    seen_test_qids.add(qid)

        selected_qids = []

        if test.test_type == TestType.APTITUDE:
            # Aptitude test: dynamically select 30 questions across Quantitative (12), Logical (10), Verbal (8)
            # 1 question per topic across all 30 Aptitude topics for maximum curriculum coverage
            topics_res = await db.execute(
                select(Topic)
                .where(Topic.subject_id.in_([1, 2, 3]))
                .order_by(Topic.subject_id, Topic.order_index)
            )
            apt_topics = topics_res.scalars().all()

            # Balanced difficulty cycle across the 30 questions
            diff_cycle = [
                DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.MEDIUM,
                DifficultyLevel.HARD, DifficultyLevel.EASY, DifficultyLevel.MEDIUM
            ]

            for idx, top in enumerate(apt_topics):
                target_diff = diff_cycle[idx % len(diff_cycle)]
                tq_res = await db.execute(
                    select(Question).where(Question.topic_id == top.id)
                )
                top_questions = tq_res.scalars().all()
                if not top_questions:
                    continue

                unseen = [q for q in top_questions if q.id not in seen_test_qids]
                candidate = None
                if unseen:
                    matching = [q for q in unseen if q.difficulty == target_diff]
                    candidate = random.choice(matching) if matching else random.choice(unseen)
                else:
                    # Pool exhausted for this topic for this student: fallback to any question
                    matching = [q for q in top_questions if q.difficulty == target_diff]
                    candidate = random.choice(matching) if matching else random.choice(top_questions)

                if candidate:
                    selected_qids.append(candidate.id)
                    seen_test_qids.add(candidate.id)

            # Ensure 30 questions in case of missing topic
            if len(selected_qids) < 30:
                fill_res = await db.execute(
                    select(Question.id)
                    .join(Topic, Question.topic_id == Topic.id)
                    .where(Topic.subject_id.in_([1, 2, 3]))
                    .where(Question.id.notin_(selected_qids))
                )
                fill_ids = fill_res.scalars().all()
                if fill_ids:
                    needed = 30 - len(selected_qids)
                    selected_qids.extend(random.sample(fill_ids, min(needed, len(fill_ids))))
        else:
            # Other test types: select from test's blueprint or available questions
            tq_ids = [tq.question_id for tq in test.test_questions if tq.question_id]
            target_count = min(len(tq_ids) if tq_ids else 30, 30)
            if tq_ids:
                unseen = [qid for qid in tq_ids if qid not in seen_test_qids]
                if len(unseen) >= target_count:
                    selected_qids = random.sample(unseen, target_count)
                else:
                    seen = [qid for qid in tq_ids if qid in seen_test_qids]
                    selected_qids = list(unseen) + random.sample(seen, min(target_count - len(unseen), len(seen)))
            else:
                all_q_res = await db.execute(select(Question.id).limit(target_count))
                selected_qids = all_q_res.scalars().all()

        if test.randomize_questions:
            random.shuffle(selected_qids)

        attempt.question_order = selected_qids
        await db.commit()
        await db.refresh(attempt)

    # Build questions list directly from attempt.question_order
    order_ids = attempt.question_order or []
    q_result = await db.execute(
        select(Question)
        .where(Question.id.in_(order_ids))
        .options(selectinload(Question.options))
    )
    q_map = {q.id: q for q in q_result.scalars().all()}

    questions_out = []
    from app.services.adaptive_engine import AdaptiveEngine
    for qid in order_ids:
        q = q_map.get(qid)
        if q:
            # Deterministic option shuffle based on attempt and question ID so options do not jump on page refresh
            rng = random.Random(attempt.id * 1000 + q.id)
            opts = list(q.options)
            rng.shuffle(opts)
            questions_out.append({
                "id": q.id,
                "text": q.text,
                "question_type": q.question_type.value,
                "difficulty": q.difficulty.value,
                "points": q.points,
                "options": [{"id": o.id, "text": o.text, "order_index": idx} for idx, o in enumerate(opts)],
            })
            await AdaptiveEngine.record_question_exposure(db, profile.id, q.id)

    return TestStartResponse(
        attempt_id=attempt.id,
        test_id=test_id,
        expires_at=attempt.expires_at,
        questions=questions_out,
    )


@router.post("/tests/submit", response_model=TestAttemptResult)
async def submit_test(
    payload: TestSubmitRequest,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    from app.services.adaptive_engine import AdaptiveEngine
    result = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.id == payload.attempt_id)
        .where(TestAttempt.student_id == profile.id)
        .options(selectinload(TestAttempt.test).selectinload(Test.test_questions))
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.status != AttemptStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Test already submitted")

    # Server-side timer check
    now = datetime.now(timezone.utc)
    if attempt.expires_at and now > attempt.expires_at.replace(tzinfo=timezone.utc):
        attempt.status = AttemptStatus.TIMED_OUT
        attempt.submitted_at = now
        await db.commit()
        raise HTTPException(status_code=400, detail="Test time has expired")

    # Grade answers server-side — NEVER trust client score
    total_score = 0.0
    max_score = 0.0

    for ans in payload.answers:
        q_result = await db.execute(
            select(Question)
            .where(Question.id == ans.question_id)
            .options(selectinload(Question.options))
        )
        question = q_result.scalar_one_or_none()
        if not question:
            continue

        correct_option = next((o for o in question.options if o.is_correct), None)
        is_correct = correct_option and (ans.selected_option_id == correct_option.id)
        marks_awarded = question.points if is_correct else 0
        max_score += question.points
        total_score += marks_awarded

        db.add(TestAnswer(
            attempt_id=attempt.id,
            question_id=ans.question_id,
            selected_option_id=ans.selected_option_id,
            is_correct=is_correct,
            marks_awarded=marks_awarded,
            time_taken_seconds=ans.time_taken_seconds,
            answered_at=now,
        ))

        # Update question stats
        question.attempt_count += 1
        if is_correct:
            question.correct_count += 1

        # Record question exposure result in adaptive engine
        await AdaptiveEngine.update_question_exposure_result(db, profile.id, ans.question_id, is_correct)

    percentage = (total_score / max_score * 100) if max_score > 0 else 0.0
    attempt.score = total_score
    attempt.max_score = max_score
    attempt.percentage = percentage
    attempt.status = AttemptStatus.GRADED
    attempt.submitted_at = now

    # Update student profile scores dynamically with authoritative scoring engine
    await calculate_and_sync_student_scores(db, profile)
    await db.refresh(attempt)

    return TestAttemptResult(
        id=attempt.id,
        test_id=attempt.test_id,
        student_id=attempt.student_id,
        status=attempt.status,
        started_at=attempt.started_at,
        submitted_at=attempt.submitted_at,
        score=attempt.score,
        max_score=attempt.max_score,
        percentage=attempt.percentage,
        passed=attempt.score >= attempt.test.passing_marks if attempt.test else None,
    )


@router.get("/tests/history", response_model=List[dict])
async def test_history(
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.student_id == profile.id)
        .where(TestAttempt.status.in_([AttemptStatus.GRADED, AttemptStatus.TIMED_OUT]))
        .order_by(TestAttempt.submitted_at.desc())
        .options(selectinload(TestAttempt.test))
        .limit(50)
    )
    attempts = result.scalars().all()
    return [
        {
            "attempt_id": a.id,
            "test_id": a.test_id,
            "test_title": a.test.title if a.test else "Unknown",
            "score": a.score,
            "max_score": a.max_score,
            "percentage": a.percentage,
            "status": a.status.value,
            "submitted_at": a.submitted_at,
        }
        for a in attempts
    ]


@router.get("/tests/attempts/{attempt_id}")
async def get_test_attempt_review(
    attempt_id: int,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.id == attempt_id)
        .where(TestAttempt.student_id == profile.id)
        .options(
            selectinload(TestAttempt.test),
            selectinload(TestAttempt.answers),
        )
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    # Branch by test type: CODING vs APTITUDE/MCQ
    if attempt.test and attempt.test.test_type == TestType.CODING:
        target_c_ids = attempt.question_order or []
        if not target_c_ids:
            sub_res = await db.execute(
                select(CodeSubmission.coding_question_id)
                .where(CodeSubmission.attempt_id == attempt.id)
            )
            target_c_ids = [r for r in set(sub_res.scalars().all()) if r]

        if not target_c_ids:
            tq_result = await db.execute(
                select(TestQuestion)
                .where(TestQuestion.test_id == attempt.test_id)
            )
            target_c_ids = [tq.coding_question_id for tq in tq_result.scalars().all() if tq.coding_question_id]

        c_result = await db.execute(
            select(CodingQuestion)
            .where(CodingQuestion.id.in_(target_c_ids))
            .options(selectinload(CodingQuestion.test_cases))
        )
        c_map = {cq.id: cq for cq in c_result.scalars().all()}
        coding_questions = [c_map[cid] for cid in target_c_ids if cid in c_map]

        # Fetch all submissions for this attempt
        subs_res = await db.execute(
            select(CodeSubmission)
            .where(CodeSubmission.attempt_id == attempt.id)
            .order_by(CodeSubmission.submitted_at.desc())
        )
        all_subs = subs_res.scalars().all()
        best_subs = {}
        for s in all_subs:
            if s.coding_question_id not in best_subs or (s.score or 0) > (best_subs[s.coding_question_id].score or 0):
                best_subs[s.coding_question_id] = s

        per_q_marks = round(float(attempt.test.total_marks or 100) / max(1, len(coding_questions)), 1)

        review_questions = []
        for cq in coding_questions:
            sub = best_subs.get(cq.id)
            is_accepted = bool(sub and sub.verdict.value == "ACCEPTED")
            marks_awarded = sub.score if sub else 0.0

            review_questions.append({
                "question_id": cq.id,
                "title": cq.title,
                "text": cq.problem_statement,
                "difficulty": cq.difficulty,
                "points": per_q_marks,
                "marks_awarded": marks_awarded,
                "is_correct": is_accepted,
                "verdict": sub.verdict.value if sub else "NOT_ATTEMPTED",
                "language": sub.language if sub else None,
                "source_code": sub.source_code if sub else None,
                "test_cases_passed": sub.test_cases_passed if sub else 0,
                "test_cases_total": sub.test_cases_total if sub else len(cq.test_cases),
                "constraints": cq.constraints,
                "explanation": cq.explanation,
                "options": [],
            })

        passed = None
        if attempt.test and attempt.test.passing_marks is not None:
            passed = attempt.score >= attempt.test.passing_marks

        return {
            "attempt_id": attempt.id,
            "test_id": attempt.test_id,
            "test_title": attempt.test.title if attempt.test else "",
            "test_type": attempt.test.test_type.value if attempt.test else "",
            "status": attempt.status.value,
            "score": attempt.score,
            "max_score": attempt.max_score,
            "percentage": attempt.percentage,
            "passed": passed,
            "passing_marks": attempt.test.passing_marks if attempt.test else None,
            "started_at": attempt.started_at,
            "submitted_at": attempt.submitted_at,
            "total_questions": len(review_questions),
            "correct_answers": sum(1 for q in review_questions if q["is_correct"]),
            "questions": review_questions,
        }

    # Standard MCQ questions review for APTITUDE and other test types
    answers_map = {ans.question_id: ans for ans in attempt.answers}

    # Load questions for this attempt from attempt.question_order or attempt.answers
    target_qids = attempt.question_order or [ans.question_id for ans in attempt.answers if ans.question_id]
    if not target_qids:
        tq_result = await db.execute(
            select(TestQuestion)
            .where(TestQuestion.test_id == attempt.test_id)
            .options(
                selectinload(TestQuestion.question).selectinload(Question.options)
            )
        )
        test_questions = [tq.question for tq in tq_result.scalars().all() if tq.question]
    else:
        q_result = await db.execute(
            select(Question)
            .where(Question.id.in_(target_qids))
            .options(selectinload(Question.options))
        )
        q_dict = {q.id: q for q in q_result.scalars().all()}
        test_questions = [q_dict[qid] for qid in target_qids if qid in q_dict]

    review_questions = []
    for q in test_questions:
        if not q:
            continue
        ans = answers_map.get(q.id)
        correct_opt = next((o for o in q.options if o.is_correct), None)

        review_questions.append({
            "question_id": q.id,
            "title": None,
            "text": q.text,
            "points": q.points,
            "selected_option_id": ans.selected_option_id if ans else None,
            "correct_option_id": correct_opt.id if correct_opt else None,
            "is_correct": ans.is_correct if ans else False,
            "marks_awarded": ans.marks_awarded if ans else 0.0,
            "explanation": q.explanation,
            "options": [{"id": o.id, "text": o.text} for o in q.options],
        })

    passed = None
    if attempt.test and attempt.test.passing_marks is not None:
        passed = attempt.score >= attempt.test.passing_marks

    return {
        "attempt_id": attempt.id,
        "test_id": attempt.test_id,
        "test_title": attempt.test.title if attempt.test else "",
        "test_type": attempt.test.test_type.value if attempt.test else "",
        "status": attempt.status.value,
        "score": attempt.score,
        "max_score": attempt.max_score,
        "percentage": attempt.percentage,
        "passed": passed,
        "passing_marks": attempt.test.passing_marks if attempt.test else None,
        "started_at": attempt.started_at,
        "submitted_at": attempt.submitted_at,
        "total_questions": len(review_questions),
        "correct_answers": sum(1 for q in review_questions if q["is_correct"]),
        "questions": review_questions,
    }


@router.get("/progress", response_model=List[TopicProgressOut])
async def student_progress(
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TopicProgress)
        .where(TopicProgress.student_id == profile.id)
        .options(selectinload(TopicProgress.topic))
    )
    progresses = result.scalars().all()
    return [
        TopicProgressOut(
            topic_id=p.topic_id,
            topic_name=p.topic.name if p.topic else None,
            lessons_completed=p.lessons_completed,
            total_lessons=p.total_lessons,
            questions_attempted=p.questions_attempted,
            questions_correct=p.questions_correct,
            skill_rating=p.skill_rating,
            accuracy=(p.questions_correct / p.questions_attempted * 100) if p.questions_attempted > 0 else None,
            last_practiced=p.last_practiced,
        )
        for p in progresses
    ]


# ─────────────────────────────── Helpers ────────────────────────────────

async def _get_or_create_topic_progress(db: AsyncSession, student_id: int, topic_id: int) -> TopicProgress:
    result = await db.execute(
        select(TopicProgress)
        .where(TopicProgress.student_id == student_id)
        .where(TopicProgress.topic_id == topic_id)
    )
    tp = result.scalar_one_or_none()
    if not tp:
        # Count total lessons
        lesson_count = await db.execute(
            select(func.count(Lesson.id)).where(Lesson.topic_id == topic_id)
        )
        tp = TopicProgress(
            student_id=student_id,
            topic_id=topic_id,
            total_lessons=lesson_count.scalar() or 0,
        )
        db.add(tp)
        await db.flush()
    return tp
