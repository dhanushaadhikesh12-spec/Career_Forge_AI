"""
Trainer routes: dashboard, batches, tests, student analytics.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.api.deps import get_trainer_profile
from app.models.user import TrainerProfile, Batch, BatchMembership, StudentProfile, User, TopicProgress
from app.models.test import Test, TestAttempt, TestQuestion, TestStatus, AttemptStatus, ProctoringEvent
from app.models.content import Question, QuestionOption, Subject, Topic, Lesson
from app.models.chat import AIChatSession, AIChatMessage

from app.schemas.auth import BatchOut, BatchCreate
from app.schemas.test import TestCreate, TestOut, ProctoringEventOut
from pydantic import BaseModel, ConfigDict
from app.core.config import settings
from app.services.ai.assistant import process_trainer_query, AssistantResponse, ChatMessage
from app.services.ai.provider import get_llm_provider
from app.ml.feature_engineering import extract_student_features
from app.ml.readiness_model import get_readiness_model
from app.ml.training import retrain_readiness_model
import logging

router = APIRouter(prefix="/trainers", tags=["Trainer"])
logger = logging.getLogger(__name__)


# ─────────────────────────────── Dashboard ────────────────────────────────

@router.get("/dashboard")
async def trainer_dashboard(
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    # Get trainer's batches
    batches_result = await db.execute(
        select(Batch).where(Batch.trainer_id == profile.id).where(Batch.is_active == True)
    )
    batches = batches_result.scalars().all()
    batch_ids = [b.id for b in batches]

    # Count students
    student_count = 0
    if batch_ids:
        sc = await db.execute(
            select(func.count(BatchMembership.id))
            .where(BatchMembership.batch_id.in_(batch_ids))
            .where(BatchMembership.is_active == True)
        )
        student_count = sc.scalar() or 0

    # Recent tests
    tests_result = await db.execute(
        select(Test)
        .where(Test.created_by == profile.user_id)
        .order_by(Test.created_at.desc())
        .limit(5)
    )
    recent_tests = tests_result.scalars().all()

    # Average scores across batches
    avg_scores = []
    for b in batches:
        members = await db.execute(
            select(BatchMembership.student_id)
            .where(BatchMembership.batch_id == b.id)
            .where(BatchMembership.is_active == True)
        )
        student_ids = [m[0] for m in members]
        if student_ids:
            avg = await db.execute(
                select(func.avg(TestAttempt.percentage))
                .where(TestAttempt.student_id.in_(student_ids))
                .where(TestAttempt.status == AttemptStatus.GRADED)
            )
            avg_scores.append({
                "batch_id": b.id,
                "batch_name": b.name,
                "avg_score": round(avg.scalar() or 0, 1),
                "student_count": len(student_ids),
            })

    return {
        "trainer": {
            "id": profile.id,
            "full_name": profile.user.full_name if hasattr(profile, "user") else "",
            "specialization": profile.specialization,
        },
        "batch_count": len(batches),
        "student_count": student_count,
        "recent_tests": [
            {"id": t.id, "title": t.title, "status": t.status.value, "created_at": t.created_at}
            for t in recent_tests
        ],
        "batch_performance": avg_scores,
    }


# ─────────────────────────────── Batches ────────────────────────────────

@router.get("/batches", response_model=List[BatchOut])
async def list_batches(
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Batch).where(Batch.trainer_id == profile.id).order_by(Batch.created_at.desc())
    )
    batches = result.scalars().all()
    out = []
    for b in batches:
        count = await db.execute(
            select(func.count(BatchMembership.id))
            .where(BatchMembership.batch_id == b.id)
            .where(BatchMembership.is_active == True)
        )
        out.append(BatchOut(
            id=b.id,
            name=b.name,
            description=b.description,
            is_active=b.is_active,
            start_date=b.start_date,
            end_date=b.end_date,
            created_at=b.created_at,
            member_count=count.scalar() or 0,
        ))
    return out


@router.post("/batches", response_model=BatchOut, status_code=status.HTTP_201_CREATED)
async def create_batch(
    payload: BatchCreate,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    batch = Batch(
        name=payload.name,
        description=payload.description,
        trainer_id=profile.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(batch)
    await db.commit()
    await db.refresh(batch)
    return BatchOut(
        id=batch.id, name=batch.name, description=batch.description,
        is_active=batch.is_active, start_date=batch.start_date,
        end_date=batch.end_date, created_at=batch.created_at, member_count=0,
    )


@router.post("/batches/{batch_id}/students/{student_id}")
async def add_student_to_batch(
    batch_id: int,
    student_id: int,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    # Authorization: batch must belong to trainer
    batch = await _get_trainer_batch(db, batch_id, profile.id)

    # Check student exists
    student = await db.execute(select(StudentProfile).where(StudentProfile.id == student_id))
    if not student.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Student not found")

    existing = await db.execute(
        select(BatchMembership)
        .where(BatchMembership.batch_id == batch_id)
        .where(BatchMembership.student_id == student_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Student already in batch")

    db.add(BatchMembership(batch_id=batch_id, student_id=student_id))
    await db.commit()
    return {"message": "Student added to batch"}


@router.get("/batches/{batch_id}/students")
async def list_batch_students(
    batch_id: int,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    await _get_trainer_batch(db, batch_id, profile.id)
    result = await db.execute(
        select(StudentProfile)
        .join(BatchMembership, BatchMembership.student_id == StudentProfile.id)
        .where(BatchMembership.batch_id == batch_id)
        .where(BatchMembership.is_active == True)
        .options(selectinload(StudentProfile.user))
    )
    students = result.scalars().all()
    return [
        {
            "id": s.id,
            "full_name": s.user.full_name,
            "email": s.user.email,
            "total_score": s.total_score,
            "aptitude_score": s.aptitude_score,
            "coding_score": s.coding_score,
            "streak_days": s.streak_days,
        }
        for s in students
    ]


# ─────────────────────────────── Tests ────────────────────────────────

@router.get("/tests", response_model=List[TestOut])
async def list_tests(
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Test)
        .where(Test.created_by == profile.user_id)
        .order_by(Test.created_at.desc())
    )
    tests = result.scalars().all()
    out = []
    for t in tests:
        q_count = await db.execute(
            select(func.count(TestQuestion.id)).where(TestQuestion.test_id == t.id)
        )
        out.append(TestOut(
            id=t.id, title=t.title, description=t.description,
            test_type=t.test_type, status=t.status, batch_id=t.batch_id,
            duration_minutes=t.duration_minutes, total_marks=t.total_marks,
            passing_marks=t.passing_marks, instructions=t.instructions,
            randomize_questions=t.randomize_questions,
            show_results_immediately=t.show_results_immediately,
            scheduled_at=t.scheduled_at, created_at=t.created_at,
            question_count=q_count.scalar() or 0,
        ))
    return out


@router.post("/tests", response_model=TestOut, status_code=status.HTTP_201_CREATED)
async def create_test(
    payload: TestCreate,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    if payload.batch_id:
        await _get_trainer_batch(db, payload.batch_id, profile.id)

    test = Test(
        title=payload.title,
        description=payload.description,
        test_type=payload.test_type,
        batch_id=payload.batch_id,
        created_by=profile.user_id,
        duration_minutes=payload.duration_minutes,
        total_marks=payload.total_marks,
        passing_marks=payload.passing_marks,
        instructions=payload.instructions,
        randomize_questions=payload.randomize_questions,
        show_results_immediately=payload.show_results_immediately,
        scheduled_at=payload.scheduled_at,
        status=TestStatus.DRAFT,
    )
    db.add(test)
    await db.flush()

    for i, qid in enumerate(payload.question_ids):
        q = await db.execute(select(Question).where(Question.id == qid))
        if q.scalar_one_or_none():
            db.add(TestQuestion(test_id=test.id, question_id=qid, order_index=i, marks=1))

    await db.commit()
    await db.refresh(test)

    return TestOut(
        id=test.id, title=test.title, description=test.description,
        test_type=test.test_type, status=test.status, batch_id=test.batch_id,
        duration_minutes=test.duration_minutes, total_marks=test.total_marks,
        passing_marks=test.passing_marks, instructions=test.instructions,
        randomize_questions=test.randomize_questions,
        show_results_immediately=test.show_results_immediately,
        scheduled_at=test.scheduled_at, created_at=test.created_at,
        question_count=len(payload.question_ids),
    )


@router.post("/tests/{test_id}/publish")
async def publish_test(
    test_id: int,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    test = await _get_trainer_test(db, test_id, profile.user_id)
    test.status = TestStatus.PUBLISHED
    await db.commit()
    return {"message": "Test published"}


@router.get("/tests/{test_id}/results")
async def test_results(
    test_id: int,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    await _get_trainer_test(db, test_id, profile.user_id)
    result = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.test_id == test_id)
        .where(TestAttempt.status.in_([AttemptStatus.GRADED, AttemptStatus.TIMED_OUT]))
        .options(selectinload(TestAttempt.test))
    )
    attempts = result.scalars().all()

    # Get student names
    out = []
    for a in attempts:
        student = await db.execute(
            select(StudentProfile).where(StudentProfile.id == a.student_id)
            .options(selectinload(StudentProfile.user))
        )
        s = student.scalar_one_or_none()

        # Proctoring summary
        pc = await db.execute(
            select(func.count(ProctoringEvent.id)).where(ProctoringEvent.attempt_id == a.id)
        )
        violation_count = pc.scalar() or 0

        out.append({
            "attempt_id": a.id,
            "student_id": a.student_id,
            "student_name": s.user.full_name if s else "Unknown",
            "score": a.score,
            "max_score": a.max_score,
            "percentage": a.percentage,
            "status": a.status.value,
            "submitted_at": a.submitted_at,
            "violation_count": violation_count,
        })
    return out


@router.get("/tests/{test_id}/attempts/{attempt_id}/proctoring", response_model=List[ProctoringEventOut])
async def get_proctoring_events(
    test_id: int,
    attempt_id: int,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    await _get_trainer_test(db, test_id, profile.user_id)
    result = await db.execute(
        select(ProctoringEvent)
        .where(ProctoringEvent.attempt_id == attempt_id)
        .order_by(ProctoringEvent.occurred_at)
    )
    return result.scalars().all()


# ─────────────────────────────── Questions (Trainer) ────────────────────────────────

@router.get("/questions")
async def list_questions(
    topic_id: Optional[int] = None,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    query = select(Question).options(selectinload(Question.options), selectinload(Question.topic))
    if topic_id:
        query = query.where(Question.topic_id == topic_id)
    result = await db.execute(query.order_by(Question.created_at.desc()).limit(100))
    questions = result.scalars().all()
    return [
        {
            "id": q.id,
            "text": q.text,
            "topic_id": q.topic_id,
            "topic_name": q.topic.name if q.topic else None,
            "difficulty": q.difficulty.value,
            "points": q.points,
            "attempt_count": q.attempt_count,
            "correct_count": q.correct_count,
            "accuracy": round(q.correct_count / q.attempt_count * 100, 1) if q.attempt_count > 0 else None,
        }
        for q in questions
    ]


# ─────────────────────────────── Step 2: Advanced Trainer Analytics ────────────────────────────────

@router.get("/analytics/overview")
async def trainer_analytics_overview(
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Batch-level overview: aggregate aptitude, coding, test KPIs and at-risk students."""
    student_ids = await _get_trainer_student_ids(db, profile.id)
    if not student_ids:
        return {
            "student_count": 0,
            "avg_aptitude_score": 0.0,
            "avg_coding_score": 0.0,
            "avg_test_score": 0.0,
            "completion_rate": 0.0,
            "at_risk_count": 0,
            "at_risk_students": [],
            "recent_activity": [],
        }

    # Query students in batches
    students_res = await db.execute(
        select(StudentProfile)
        .where(StudentProfile.id.in_(student_ids))
        .options(selectinload(StudentProfile.user))
    )
    students = students_res.scalars().all()

    avg_apt = float(np_mean([s.aptitude_score or 0.0 for s in students]))
    avg_cod = float(np_mean([s.coding_score or 0.0 for s in students]))

    # Test attempts
    attempts_res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.student_id.in_(student_ids))
        .where(TestAttempt.status == AttemptStatus.GRADED)
    )
    attempts = attempts_res.scalars().all()
    avg_test = float(np_mean([a.percentage or 0.0 for a in attempts])) if attempts else 0.0

    # At-risk students (total_score < 45 or aptitude_score < 40 or coding_score < 30)
    at_risk = []
    for s in students:
        tot = (s.aptitude_score or 0.0) * 0.5 + (s.coding_score or 0.0) * 0.5
        if tot < 45.0 or (s.aptitude_score or 0.0) < 40.0:
            at_risk.append({
                "student_id": s.id,
                "full_name": s.user.full_name if s.user else "Student",
                "email": s.user.email if s.user else "",
                "total_score": round(tot, 1),
                "aptitude_score": s.aptitude_score or 0.0,
                "coding_score": s.coding_score or 0.0,
                "primary_risk": "Low Aptitude Accuracy" if (s.aptitude_score or 0) < 40 else "Low Coding Score",
            })

    return {
        "student_count": len(students),
        "avg_aptitude_score": round(avg_apt, 1),
        "avg_coding_score": round(avg_cod, 1),
        "avg_test_score": round(avg_test, 1),
        "completion_rate": round(min(100.0, (len(attempts) / (len(students) * 2 or 1)) * 100), 1),
        "at_risk_count": len(at_risk),
        "at_risk_students": at_risk[:10],
    }


@router.get("/analytics/students/{student_id}")
async def get_student_analytics_profile(
    student_id: int,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Deep student performance profile for trainers."""
    student_ids = await _get_trainer_student_ids(db, profile.id)
    if student_id not in student_ids:
        # Check if student exists globally
        st_check = await db.execute(select(StudentProfile).where(StudentProfile.id == student_id))
        if not st_check.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Student not found")
        raise HTTPException(status_code=403, detail="Student is not enrolled in your batches")

    st_res = await db.execute(
        select(StudentProfile)
        .where(StudentProfile.id == student_id)
        .options(selectinload(StudentProfile.user))
    )
    student = st_res.scalar_one_or_none()

    # Topic progress
    prog_res = await db.execute(
        select(TopicProgress)
        .where(TopicProgress.student_id == student_id)
        .options(selectinload(TopicProgress.topic))
    )
    progress_list = prog_res.scalars().all()
    topic_metrics = []
    for p in progress_list:
        acc = round((p.questions_correct / p.questions_attempted * 100), 1) if p.questions_attempted > 0 else 0.0
        topic_metrics.append({
            "topic_id": p.topic_id,
            "topic_name": p.topic.name if p.topic else f"Topic {p.topic_id}",
            "attempted": p.questions_attempted,
            "accuracy": acc,
            "skill_rating": round(p.skill_rating or 1000.0, 1),
            "irt_ability": round(p.irt_ability or 0.0, 2),
            "recent_accuracy": round(p.recent_accuracy or 50.0, 1),
            "streak": p.streak or 0,
        })

    # Sort topics by accuracy ascending
    topic_metrics.sort(key=lambda x: x["accuracy"])
    weakest = [t for t in topic_metrics if t["attempted"] > 0][:3]
    strongest = [t for t in reversed(topic_metrics) if t["attempted"] > 0][:3]

    # Test history
    att_res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.student_id == student_id)
        .options(selectinload(TestAttempt.test), selectinload(TestAttempt.proctoring_events))
        .order_by(TestAttempt.started_at.desc())
        .limit(10)
    )
    attempts = att_res.scalars().all()
    test_history = [
        {
            "attempt_id": a.id,
            "test_title": a.test.title if a.test else "Test",
            "score": a.score,
            "max_score": a.max_score,
            "percentage": a.percentage,
            "status": a.status.value,
            "violations_count": len(a.proctoring_events),
            "date": a.started_at,
        }
        for a in attempts
    ]

    # Coding submissions
    subs_res = await db.execute(
        select(CodeSubmission)
        .where(CodeSubmission.student_id == student_id)
        .options(selectinload(CodeSubmission.coding_question))
        .order_by(CodeSubmission.submitted_at.desc())
        .limit(15)
    )
    subs = subs_res.scalars().all()
    coding_history = [
        {
            "submission_id": s.id,
            "question_title": s.coding_question.title if s.coding_question else "Problem",
            "language": s.language,
            "verdict": s.verdict.value,
            "score": s.score,
            "passed_tests": s.test_cases_passed,
            "total_tests": s.test_cases_total,
            "runtime_ms": s.runtime_ms,
            "submitted_at": s.submitted_at,
        }
        for s in subs
    ]

    return {
        "student": {
            "id": student.id,
            "full_name": student.user.full_name if student.user else "Student",
            "email": student.user.email if student.user else "",
            "aptitude_score": student.aptitude_score or 0.0,
            "coding_score": student.coding_score or 0.0,
            "total_score": student.total_score or 0.0,
            "streak_days": student.streak_days or 0,
        },
        "weak_topics": weakest,
        "strong_topics": strongest,
        "topic_metrics": topic_metrics,
        "test_history": test_history,
        "coding_history": coding_history,
    }


@router.get("/analytics/coding")
async def trainer_coding_analytics(
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Aggregate coding metrics: language breakdown, error frequencies, solve rates."""
    student_ids = await _get_trainer_student_ids(db, profile.id)
    if not student_ids:
        return {
            "total_submissions": 0,
            "accepted_submissions": 0,
            "pass_rate": 0.0,
            "language_breakdown": {},
            "verdict_breakdown": {},
        }

    subs_res = await db.execute(
        select(CodeSubmission)
        .where(CodeSubmission.student_id.in_(student_ids))
    )
    subs = subs_res.scalars().all()

    total = len(subs)
    accepted = sum(1 for s in subs if s.verdict == SubmissionVerdict.ACCEPTED)
    pass_rate = round((accepted / total * 100), 1) if total > 0 else 0.0

    lang_counts = {}
    verdict_counts = {}
    for s in subs:
        lang = s.language.lower() if s.language else "unknown"
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

        v = s.verdict.value
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    return {
        "total_submissions": total,
        "accepted_submissions": accepted,
        "pass_rate": pass_rate,
        "language_breakdown": lang_counts,
        "verdict_breakdown": verdict_counts,
    }


@router.get("/analytics/topics")
async def trainer_topics_analytics(
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Topic analytics across all students in trainer's batches."""
    student_ids = await _get_trainer_student_ids(db, profile.id)
    if not student_ids:
        return {"topics": [], "strongest": [], "weakest": []}

    res = await db.execute(
        select(
            TopicProgress.topic_id,
            Topic.name,
            func.sum(TopicProgress.questions_attempted).label("attempted"),
            func.sum(TopicProgress.questions_correct).label("correct"),
            func.avg(TopicProgress.skill_rating).label("avg_skill"),
        )
        .join(Topic, Topic.id == TopicProgress.topic_id)
        .where(TopicProgress.student_id.in_(student_ids))
        .group_by(TopicProgress.topic_id, Topic.name)
    )
    rows = res.all()

    topic_stats = []
    for r in rows:
        att = r.attempted or 0
        corr = r.correct or 0
        acc = round((corr / att * 100), 1) if att > 0 else 0.0
        topic_stats.append({
            "topic_id": r.topic_id,
            "topic_name": r.name,
            "total_attempted": att,
            "accuracy": acc,
            "avg_skill_rating": round(float(r.avg_skill or 1000.0), 1),
        })

    topic_stats.sort(key=lambda x: x["accuracy"])
    return {
        "topics": topic_stats,
        "weakest": topic_stats[:3],
        "strongest": list(reversed(topic_stats))[:3],
    }


@router.get("/analytics/malpractice/{test_id}")
async def trainer_malpractice_report(
    test_id: int,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Aggregated malpractice report for an assessment across all student attempts."""
    await _get_trainer_test(db, test_id, profile.user_id)

    att_res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.test_id == test_id)
        .options(
            selectinload(TestAttempt.proctoring_events),
            selectinload(TestAttempt.student).selectinload(StudentProfile.user)
        )
    )
    attempts = att_res.scalars().all()

    student_reports = []
    for a in attempts:
        risk_data = calculate_malpractice_risk(a.proctoring_events)
        student_name = a.student.user.full_name if a.student and a.student.user else f"Student {a.student_id}"

        student_reports.append({
            "attempt_id": a.id,
            "student_id": a.student_id,
            "student_name": student_name,
            "score": a.score,
            "percentage": a.percentage,
            "status": a.status.value,
            "risk_level": risk_data["risk_level"],
            "total_violations": risk_data["total_violations"],
            "weighted_severity": risk_data["weighted_severity_score"],
            "breakdown": risk_data["breakdown"],
            "events_timeline": [
                {
                    "event_type": ev.event_type,
                    "severity": ev.severity,
                    "occurred_at": ev.occurred_at,
                    "description": ev.description,
                }
                for ev in sorted(a.proctoring_events, key=lambda x: x.occurred_at)
            ],
        })

    # Sort highest risk first
    student_reports.sort(key=lambda x: (x["weighted_severity"], x["total_violations"]), reverse=True)

    return {
        "test_id": test_id,
        "total_attempts": len(attempts),
        "high_risk_count": sum(1 for s in student_reports if s["risk_level"] == "HIGH"),
        "medium_risk_count": sum(1 for s in student_reports if s["risk_level"] == "MEDIUM"),
        "low_risk_count": sum(1 for s in student_reports if s["risk_level"] == "LOW"),
        "student_reports": student_reports,
    }


@router.get("/analytics/clustering")
async def trainer_student_clustering(
    batch_id: Optional[int] = None,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """K-Means performance clustering across trainer's students."""
    from app.ml.clustering import cluster_students

    if batch_id:
        await _get_trainer_batch(db, batch_id, profile.id)
        student_ids = await _get_batch_student_ids(db, batch_id)
    else:
        student_ids = await _get_trainer_student_ids(db, profile.id)

    if not student_ids:
        return {"status": "INSUFFICIENT_DATA", "message": "No students found in batches", "clusters": [], "students": []}

    st_res = await db.execute(
        select(StudentProfile)
        .where(StudentProfile.id.in_(student_ids))
        .options(selectinload(StudentProfile.user))
    )
    students = st_res.scalars().all()

    student_records = []
    for s in students:
        # Compute student average test score
        t_res = await db.execute(
            select(func.avg(TestAttempt.percentage))
            .where(TestAttempt.student_id == s.id)
            .where(TestAttempt.status == AttemptStatus.GRADED)
        )
        avg_t = t_res.scalar() or 0.0

        student_records.append({
            "id": s.id,
            "full_name": s.user.full_name if s.user else "Student",
            "email": s.user.email if s.user else "",
            "aptitude_score": s.aptitude_score or 0.0,
            "coding_score": s.coding_score or 0.0,
            "avg_test_score": round(float(avg_t), 1),
            "completion_rate": 80.0,
            "streak_days": s.streak_days or 0,
        })

    return cluster_students(student_records)


@router.get("/analytics/plagiarism")
async def trainer_plagiarism_analysis(
    question_id: Optional[int] = None,
    test_id: Optional[int] = None,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Analyzes coding submissions for code similarity and flags suspected plagiarism."""
    from app.ml.plagiarism import analyze_submission_pool

    query = (
        select(CodeSubmission)
        .options(selectinload(CodeSubmission.student).selectinload(StudentProfile.user))
    )
    if question_id:
        query = query.where(CodeSubmission.coding_question_id == question_id)
    if test_id:
        query = query.where(CodeSubmission.attempt_id.in_(
            select(TestAttempt.id).where(TestAttempt.test_id == test_id)
        ))

    res = await db.execute(query.order_by(CodeSubmission.submitted_at.desc()).limit(100))
    subs = res.scalars().all()

    submission_pool = []
    for s in subs:
        name = s.student.user.full_name if s.student and s.student.user else f"Student {s.student_id}"
        submission_pool.append({
            "student_id": s.student_id,
            "student_name": name,
            "submission_id": s.id,
            "source_code": s.source_code,
            "language": s.language,
        })

    flagged_pairs = analyze_submission_pool(submission_pool)
    return {
        "total_analyzed": len(submission_pool),
        "flagged_pairs_count": len(flagged_pairs),
        "flagged_pairs": flagged_pairs,
    }


@router.get("/analytics/anomalies/{test_id}")
async def trainer_assessment_anomalies(
    test_id: int,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Runs Isolation Forest anomaly detection on assessment attempts."""
    from app.ml.anomaly import detect_assessment_anomalies

    await _get_trainer_test(db, test_id, profile.user_id)

    att_res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.test_id == test_id)
        .options(
            selectinload(TestAttempt.student).selectinload(StudentProfile.user),
            selectinload(TestAttempt.proctoring_events),
            selectinload(TestAttempt.test)
        )
    )
    attempts = att_res.scalars().all()

    attempt_records = []
    for a in attempts:
        name = a.student.user.full_name if a.student and a.student.user else f"Student {a.student_id}"
        dur = (a.submitted_at - a.started_at).total_seconds() if (a.submitted_at and a.started_at) else 300.0

        # Count submissions
        sub_count_res = await db.execute(
            select(func.count(CodeSubmission.id)).where(CodeSubmission.attempt_id == a.id)
        )
        sc = sub_count_res.scalar() or 1

        attempt_records.append({
            "attempt_id": a.id,
            "student_id": a.student_id,
            "student_name": name,
            "test_id": test_id,
            "test_title": a.test.title if a.test else "Assessment",
            "duration_seconds": max(10, int(dur)),
            "percentage": a.percentage or 0.0,
            "violation_count": len(a.proctoring_events),
            "submission_count": sc,
            "avg_time_per_question": max(5, int(dur / 5.0)),
        })

    return detect_assessment_anomalies(attempt_records)


# ────────────────────── AI Assistant & Placement Readiness ────────────────────

class AIChatRequest(BaseModel):
    query: str
    session_id: Optional[int] = None
    conversation_history: Optional[List[ChatMessage]] = None


class AIChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    role: str
    content: str
    tool_name: Optional[str] = None
    tool_result_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class AIChatSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trainer_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class AIChatSessionDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trainer_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[AIChatMessageOut]


class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Conversation"


class UpdateSessionRequest(BaseModel):
    title: str


@router.get("/assistant/sessions", response_model=List[AIChatSessionOut])
async def list_trainer_chat_sessions(
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Lists persistent chat sessions for authenticated trainer."""
    from sqlalchemy import func
    # Use a subquery count instead of loading all message objects
    msg_count_sub = (
        select(func.count(AIChatMessage.id))
        .where(AIChatMessage.session_id == AIChatSession.id)
        .correlate(AIChatSession)
        .scalar_subquery()
    )
    result = await db.execute(
        select(AIChatSession, msg_count_sub.label("msg_count"))
        .where(AIChatSession.trainer_id == profile.id)
        .order_by(AIChatSession.updated_at.desc())
    )
    rows = result.all()
    return [
        AIChatSessionOut(
            id=s.id,
            trainer_id=s.trainer_id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=count,
        )
        for s, count in rows
    ]


@router.post("/assistant/sessions", response_model=AIChatSessionOut)
async def create_trainer_chat_session(
    req: CreateSessionRequest,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new persistent chat session for the trainer."""
    now = datetime.now(timezone.utc)
    session = AIChatSession(
        trainer_id=profile.id,
        title=req.title or "New Conversation",
        created_at=now,
        updated_at=now,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return AIChatSessionOut(
        id=session.id,
        trainer_id=session.trainer_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=0,
    )


@router.get("/assistant/sessions/{session_id}", response_model=AIChatSessionDetailOut)
async def get_trainer_chat_session(
    session_id: int,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves conversation history for a specific session with trainer cohort isolation."""
    result = await db.execute(
        select(AIChatSession)
        .where(AIChatSession.id == session_id)
        .options(selectinload(AIChatSession.messages))
    )
    session = result.scalar_one_or_none()
    if not session or session.trainer_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or unauthorized.",
        )
    return session


@router.patch("/assistant/sessions/{session_id}", response_model=AIChatSessionOut)
async def update_trainer_chat_session(
    session_id: int,
    req: UpdateSessionRequest,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Renames an existing chat session."""
    result = await db.execute(
        select(AIChatSession)
        .where(AIChatSession.id == session_id)
        .options(selectinload(AIChatSession.messages))
    )
    session = result.scalar_one_or_none()
    if not session or session.trainer_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or unauthorized.",
        )
    session.title = req.title.strip()
    session.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session)
    return AIChatSessionOut(
        id=session.id,
        trainer_id=session.trainer_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=len(session.messages),
    )


@router.delete("/assistant/sessions/{session_id}")
async def delete_trainer_chat_session(
    session_id: int,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a chat session and its persistent message history."""
    result = await db.execute(
        select(AIChatSession).where(AIChatSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session or session.trainer_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or unauthorized.",
        )
    await db.delete(session)
    await db.commit()
    return {"status": "DELETED", "session_id": session_id}


@router.post("/assistant/chat", response_model=AssistantResponse)
async def trainer_assistant_chat(
    req: AIChatRequest,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Trainer AI Assistant powered by Gemma 12B via Ollama.
    Supports persistent multi-turn chat sessions with trainer cohort authorization.
    """
    now = datetime.now(timezone.utc)
    session: Optional[AIChatSession] = None

    if req.session_id:
        s_res = await db.execute(
            select(AIChatSession)
            .where(AIChatSession.id == req.session_id)
            .options(selectinload(AIChatSession.messages))
        )
        session = s_res.scalar_one_or_none()
        if not session or session.trainer_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found or unauthorized.",
            )
    else:
        # Auto-create session
        title_snippet = req.query[:45].strip()
        if len(req.query) > 45:
            title_snippet += "..."
        session = AIChatSession(
            trainer_id=profile.id,
            title=title_snippet or "New Conversation",
            created_at=now,
            updated_at=now,
        )
        db.add(session)
        await db.flush()

    # Reconstruct history if not passed
    history = req.conversation_history
    if history is None and session and hasattr(session, "messages"):
        history = [
            ChatMessage(role=m.role, content=m.content)
            for m in session.messages
        ]

    # Persist user query
    user_msg = AIChatMessage(
        session_id=session.id,
        role="user",
        content=req.query,
        created_at=now,
    )
    db.add(user_msg)
    await db.flush()

    # Execute secure AI pipeline
    response = await process_trainer_query(
        query=req.query,
        trainer_profile=profile,
        db=db,
        conversation_history=history,
    )

    # Persist assistant reply
    asst_msg = AIChatMessage(
        session_id=session.id,
        role="assistant",
        content=response.reply,
        tool_name=response.tool_called,
        tool_result_metadata=response.structured_data,
        created_at=datetime.now(timezone.utc),
    )
    db.add(asst_msg)

    # Update session metadata
    session.updated_at = datetime.now(timezone.utc)
    if session.title == "New Conversation":
        snippet = req.query[:45].strip()
        session.title = snippet + ("..." if len(req.query) > 45 else "")

    await db.commit()

    response.session_id = session.id
    return response


@router.get("/health-check")
async def trainer_question_bank_health(
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Administrative Question Bank Health Check."""
    from app.utils.health_check import run_health_check
    return await run_health_check(db)



@router.get("/assistant/status")
async def trainer_assistant_status(
    profile: TrainerProfile = Depends(get_trainer_profile),
):
    """Checks Ollama connection and Gemma 12B model availability."""
    provider = get_llm_provider()
    is_avail = await provider.is_available()
    return {
        "available": is_avail,
        "provider": "ollama",
        "model": settings.OLLAMA_MODEL,
        "base_url": settings.OLLAMA_BASE_URL,
    }


@router.get("/analytics/readiness")
async def trainer_batch_readiness(
    batch_id: Optional[int] = None,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Batch placement readiness predictions using XGBoost multi-dimensional classifier.
    """
    if batch_id is not None:
        await _get_trainer_batch(db, batch_id, profile.id)
        student_ids = await _get_batch_student_ids(db, batch_id)
    else:
        student_ids = await _get_trainer_student_ids(db, profile.id)

    if not student_ids:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": "No students found in the selected batch.",
            "total_students": 0,
            "readiness_summary": {
                "placement_ready_count": 0,
                "developing_count": 0,
                "needs_improvement_count": 0,
            },
            "students": [],
        }

    model = get_readiness_model()
    predictions = []
    cat_counts = {"PLACEMENT_READY": 0, "DEVELOPING": 0, "NEEDS_IMPROVEMENT": 0}

    for s_id in student_ids:
        feats_info = await extract_student_features(db, s_id)
        pred = model.predict(feats_info)
        cat = pred.get("readiness_category", "NEEDS_IMPROVEMENT")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

        u_res = await db.execute(
            select(User.full_name, User.email)
            .join(StudentProfile, StudentProfile.user_id == User.id)
            .where(StudentProfile.id == s_id)
        )
        row = u_res.first()
        full_name = row[0] if row else f"Student {s_id}"
        email = row[1] if row else ""

        predictions.append({
            "student_id": s_id,
            "full_name": full_name,
            "email": email,
            "readiness_score": pred.get("readiness_score", 0.0),
            "readiness_category": cat,
            "confidence": pred.get("confidence", 0.0),
            "status": pred.get("status", "READY"),
            "contributing_factors": pred.get("contributing_factors", {}),
            "probabilities": pred.get("probabilities", {}),
        })

    predictions.sort(key=lambda x: x["readiness_score"], reverse=True)
    return {
        "status": "SUCCESS",
        "total_students": len(predictions),
        "readiness_summary": {
            "placement_ready_count": cat_counts["PLACEMENT_READY"],
            "developing_count": cat_counts["DEVELOPING"],
            "needs_improvement_count": cat_counts["NEEDS_IMPROVEMENT"],
        },
        "students": predictions,
    }


@router.get("/analytics/readiness/{student_id}")
async def trainer_student_readiness(
    student_id: int,
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Detailed placement readiness prediction and feature attributions for a single student.
    Enforces trainer batch authorization.
    """
    student_ids = await _get_trainer_student_ids(db, profile.id)
    if student_id not in student_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Student {student_id} is not enrolled in your batches.",
        )

    feats_info = await extract_student_features(db, student_id)
    model = get_readiness_model()
    prediction = model.predict(feats_info)

    u_res = await db.execute(
        select(User.full_name, User.email)
        .join(StudentProfile, StudentProfile.user_id == User.id)
        .where(StudentProfile.id == student_id)
    )
    row = u_res.first()

    return {
        "student_id": student_id,
        "full_name": row[0] if row else f"Student {student_id}",
        "email": row[1] if row else "",
        "prediction": prediction,
    }


@router.post("/analytics/retrain-readiness")
async def trainer_retrain_readiness_endpoint(
    profile: TrainerProfile = Depends(get_trainer_profile),
    db: AsyncSession = Depends(get_db),
):
    """Retrains the placement readiness model with latest student cohort performance."""
    return await retrain_readiness_model(db)


# ─────────────────────────────── Helpers ────────────────────────────────

def np_mean(vals: List[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


async def _get_trainer_student_ids(db: AsyncSession, trainer_id: int) -> List[int]:
    batches_res = await db.execute(
        select(Batch.id).where(Batch.trainer_id == trainer_id).where(Batch.is_active == True)
    )
    batch_ids = [b[0] for b in batches_res.fetchall()]
    if not batch_ids:
        return []

    mem_res = await db.execute(
        select(BatchMembership.student_id)
        .where(BatchMembership.batch_id.in_(batch_ids))
        .where(BatchMembership.is_active == True)
    )
    return list(set(m[0] for m in mem_res.fetchall()))


async def _get_batch_student_ids(db: AsyncSession, batch_id: int) -> List[int]:
    mem_res = await db.execute(
        select(BatchMembership.student_id)
        .where(BatchMembership.batch_id == batch_id)
        .where(BatchMembership.is_active == True)
    )
    return list(set(m[0] for m in mem_res.fetchall()))


async def _get_trainer_batch(db: AsyncSession, batch_id: int, trainer_id: int) -> Batch:
    result = await db.execute(
        select(Batch)
        .where(Batch.id == batch_id)
        .where(Batch.trainer_id == trainer_id)
    )
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=403, detail="Batch not found or access denied")
    return batch


async def _get_trainer_test(db: AsyncSession, test_id: int, user_id: int) -> Test:
    result = await db.execute(
        select(Test).where(Test.id == test_id).where(Test.created_by == user_id)
    )
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=403, detail="Test not found or access denied")
    return test

