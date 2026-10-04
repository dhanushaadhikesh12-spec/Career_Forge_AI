"""
Approved Backend Tools for Trainer AI Assistant.
Provides parameter-validated, permission-enforced read-only tools.
Strictly isolates data to trainer's authorized batches.
"""
from __future__ import annotations
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.user import TrainerProfile, Batch, BatchMembership, StudentProfile, TopicProgress, User
from app.models.content import Topic, Subject
from app.models.test import Test, TestAttempt, AttemptStatus, ProctoringEvent
from app.models.coding import CodeSubmission, SubmissionVerdict
from app.ml.feature_engineering import extract_student_features
from app.ml.readiness_model import get_readiness_model
from app.ml.anomaly import detect_assessment_anomalies
from app.api.routes.proctoring import calculate_malpractice_risk

logger = logging.getLogger(__name__)


class TrainerContext:
    """Encapsulates authenticated trainer permissions and batch boundaries."""
    def __init__(self, trainer_id: int, user_id: int, authorized_batch_ids: List[int], authorized_student_ids: List[int]):
        self.trainer_id = trainer_id
        self.user_id = user_id
        self.authorized_batch_ids = authorized_batch_ids
        self.authorized_student_ids = authorized_student_ids

    def is_student_authorized(self, student_id: int) -> bool:
        return student_id in self.authorized_student_ids

    def is_batch_authorized(self, batch_id: int) -> bool:
        return batch_id in self.authorized_batch_ids


async def build_trainer_context(db: AsyncSession, trainer_profile: TrainerProfile) -> TrainerContext:
    """Builds trainer boundary context from database."""
    # Batches
    b_res = await db.execute(
        select(Batch.id).where(Batch.trainer_id == trainer_profile.id, Batch.is_active == True)
    )
    batch_ids = [row[0] for row in b_res.all()]

    # Student IDs
    student_ids: List[int] = []
    if batch_ids:
        m_res = await db.execute(
            select(BatchMembership.student_id)
            .where(BatchMembership.batch_id.in_(batch_ids), BatchMembership.is_active == True)
        )
        student_ids = [row[0] for row in m_res.all()]

    return TrainerContext(
        trainer_id=trainer_profile.id,
        user_id=trainer_profile.user_id,
        authorized_batch_ids=batch_ids,
        authorized_student_ids=student_ids,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Approved Tools Registry
# ─────────────────────────────────────────────────────────────────────────────

async def tool_get_weak_students(
    ctx: TrainerContext, db: AsyncSession, topic: Optional[str] = None, batch_id: Optional[int] = None
) -> Dict[str, Any]:
    """Finds students whose accuracy or skill in a topic is below target benchmark (60%)."""
    target_students = ctx.authorized_student_ids
    if batch_id is not None:
        if not ctx.is_batch_authorized(batch_id):
            return {"error": f"Access Denied: Batch {batch_id} is not within your authorized cohorts."}
        m_res = await db.execute(
            select(BatchMembership.student_id).where(BatchMembership.batch_id == batch_id, BatchMembership.is_active == True)
        )
        target_students = [row[0] for row in m_res.all()]

    if not target_students:
        return {"topic": topic or "All Topics", "weak_students": [], "message": "No students found in cohort."}

    query = (
        select(TopicProgress, StudentProfile, User, Topic)
        .join(StudentProfile, StudentProfile.id == TopicProgress.student_id)
        .join(User, User.id == StudentProfile.user_id)
        .join(Topic, Topic.id == TopicProgress.topic_id)
        .where(TopicProgress.student_id.in_(target_students))
    )
    if topic:
        query = query.where(Topic.name.ilike(f"%{topic}%"))

    res = await db.execute(query)
    rows = res.all()

    weak = []
    for tp, sp, u, t in rows:
        att = tp.questions_attempted
        corr = tp.questions_correct
        acc = round((corr / att * 100.0), 1) if att > 0 else 0.0
        if acc < 60.0 or tp.skill_rating < 1000.0:
            weak.append({
                "student_id": sp.id,
                "student_name": u.full_name,
                "topic_name": t.name,
                "accuracy": acc,
                "questions_attempted": att,
                "skill_rating": round(float(tp.skill_rating), 1),
            })

    weak.sort(key=lambda x: x["accuracy"])
    return {
        "topic": topic or "All Topics",
        "count": len(weak),
        "weak_students": weak[:10],
    }


async def tool_get_batch_summary(
    ctx: TrainerContext, db: AsyncSession, batch_id: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieves high-level performance metrics for a batch."""
    if batch_id is not None:
        if not ctx.is_batch_authorized(batch_id):
            return {"error": f"Access Denied: Batch {batch_id} is outside your authorized scope."}
        target_batches = [batch_id]
    else:
        target_batches = ctx.authorized_batch_ids

    if not target_batches:
        return {"error": "Trainer has no active assigned batches."}

    # Fetch batch details
    b_res = await db.execute(select(Batch).where(Batch.id.in_(target_batches)))
    batches = b_res.scalars().all()

    # Students
    st_res = await db.execute(
        select(StudentProfile, User)
        .join(User, User.id == StudentProfile.user_id)
        .join(BatchMembership, BatchMembership.student_id == StudentProfile.id)
        .where(BatchMembership.batch_id.in_(target_batches), BatchMembership.is_active == True)
    )
    students = st_res.all()
    student_ids = [sp.id for sp, u in students]

    total_students = len(students)
    if total_students == 0:
        return {
            "batch_names": [b.name for b in batches],
            "total_students": 0,
            "avg_aptitude_score": 0.0,
            "avg_coding_score": 0.0,
            "avg_test_score": 0.0,
            "at_risk_count": 0,
        }

    avg_apt = round(sum(float(sp.aptitude_score or 0.0) for sp, u in students) / total_students, 1)
    avg_cod = round(sum(float(sp.coding_score or 0.0) for sp, u in students) / total_students, 1)
    avg_total = round(sum(float(sp.total_score or 0.0) for sp, u in students) / total_students, 1)
    at_risk = sum(1 for sp, u in students if (sp.total_score or 0.0) < 50.0)

    return {
        "batch_ids": target_batches,
        "batch_names": [b.name for b in batches],
        "total_students": total_students,
        "avg_aptitude_score": avg_apt,
        "avg_coding_score": avg_cod,
        "avg_overall_score": avg_total,
        "at_risk_students_count": at_risk,
    }


async def tool_get_student_performance(
    ctx: TrainerContext, db: AsyncSession, student_id: int
) -> Dict[str, Any]:
    """Retrieves deep performance profile for a specific student with authorization enforcement."""
    if not ctx.is_student_authorized(student_id):
        return {"error": f"Access Denied: Student ID {student_id} is not enrolled in your authorized batches."}

    sp_res = await db.execute(
        select(StudentProfile, User)
        .join(User, User.id == StudentProfile.user_id)
        .where(StudentProfile.id == student_id)
    )
    row = sp_res.first()
    if not row:
        return {"error": f"Student with ID {student_id} not found."}
    sp, u = row

    # Topic breakdown
    tp_res = await db.execute(
        select(TopicProgress, Topic)
        .join(Topic, Topic.id == TopicProgress.topic_id)
        .where(TopicProgress.student_id == student_id)
    )
    topics = []
    for tp, t in tp_res.all():
        att = tp.questions_attempted
        corr = tp.questions_correct
        acc = round((corr / att * 100.0), 1) if att > 0 else 0.0
        topics.append({
            "topic_name": t.name,
            "accuracy": acc,
            "attempted": att,
            "skill_rating": round(float(tp.skill_rating), 1),
        })

    # Submissions
    sub_res = await db.execute(
        select(func.count(CodeSubmission.id), func.avg(CodeSubmission.score))
        .where(CodeSubmission.student_id == student_id)
    )
    sub_count, avg_sub_score = sub_res.first() or (0, 0.0)

    return {
        "student_id": sp.id,
        "full_name": u.full_name,
        "email": u.email,
        "overall_score": sp.total_score,
        "aptitude_score": sp.aptitude_score,
        "coding_score": sp.coding_score,
        "total_practice_questions": sum(t["attempted"] for t in topics),
        "streak_days": sp.streak_days,
        "submissions_count": sub_count or 0,
        "avg_submission_score": round(float(avg_sub_score or 0.0), 1),
        "topic_performance": sorted(topics, key=lambda x: x["accuracy"])[:5],
    }


async def tool_get_placement_readiness(
    ctx: TrainerContext, db: AsyncSession, student_id: Optional[int] = None, batch_id: Optional[int] = None
) -> Dict[str, Any]:
    """Evaluates XGBoost placement readiness for a student or batch."""
    model = get_readiness_model()

    if student_id is not None:
        if not ctx.is_student_authorized(student_id):
            return {"error": f"Access Denied: Student ID {student_id} is not in your authorized batches."}
        features_info = await extract_student_features(db, student_id)
        prediction = model.predict(features_info)

        # Get student name
        u_res = await db.execute(
            select(User.full_name)
            .join(StudentProfile, StudentProfile.user_id == User.id)
            .where(StudentProfile.id == student_id)
        )
        name = u_res.scalar_one_or_none() or f"Student {student_id}"

        return {
            "student_id": student_id,
            "student_name": name,
            "readiness": prediction,
        }

    # Batch evaluation
    target_students = ctx.authorized_student_ids
    if batch_id is not None:
        if not ctx.is_batch_authorized(batch_id):
            return {"error": f"Access Denied: Batch {batch_id} is not within your cohorts."}
        m_res = await db.execute(
            select(BatchMembership.student_id).where(BatchMembership.batch_id == batch_id, BatchMembership.is_active == True)
        )
        target_students = [row[0] for row in m_res.all()]

    results = []
    category_counts = {"NEEDS_IMPROVEMENT": 0, "DEVELOPING": 0, "PLACEMENT_READY": 0}

    for s_id in target_students[:25]:  # Bound computation
        feat = await extract_student_features(db, s_id)
        pred = model.predict(feat)
        cat = pred.get("readiness_category", "NEEDS_IMPROVEMENT")
        category_counts[cat] = category_counts.get(cat, 0) + 1

        u_res = await db.execute(
            select(User.full_name)
            .join(StudentProfile, StudentProfile.user_id == User.id)
            .where(StudentProfile.id == s_id)
        )
        name = u_res.scalar_one_or_none() or f"Student {s_id}"

        results.append({
            "student_id": s_id,
            "student_name": name,
            "readiness_score": pred.get("readiness_score", 0.0),
            "category": cat,
            "confidence": pred.get("confidence", 0.0),
        })

    ready_students = [r for r in results if r["category"] == "PLACEMENT_READY"]
    return {
        "total_evaluated": len(results),
        "category_breakdown": category_counts,
        "placement_ready_students": ready_students,
        "sample_students": results[:8],
    }


async def tool_get_at_risk_students(
    ctx: TrainerContext, db: AsyncSession, batch_id: Optional[int] = None
) -> Dict[str, Any]:
    """Identifies at-risk candidates based on scores, test failures, or high proctoring violations."""
    target_students = ctx.authorized_student_ids
    if batch_id is not None:
        if not ctx.is_batch_authorized(batch_id):
            return {"error": f"Access Denied: Batch {batch_id} is not authorized."}
        m_res = await db.execute(
            select(BatchMembership.student_id).where(BatchMembership.batch_id == batch_id, BatchMembership.is_active == True)
        )
        target_students = [row[0] for row in m_res.all()]

    if not target_students:
        return {"at_risk_students": [], "count": 0}

    sp_res = await db.execute(
        select(StudentProfile, User)
        .join(User, User.id == StudentProfile.user_id)
        .where(StudentProfile.id.in_(target_students))
    )
    rows = sp_res.all()

    at_risk = []
    for sp, u in rows:
        tot = sp.total_score or 0.0
        apt = sp.aptitude_score or 0.0
        cod = sp.coding_score or 0.0
        if tot < 50.0 or apt < 45.0 or cod < 40.0:
            reasons = []
            if tot < 50.0:
                reasons.append(f"Low overall score ({tot}%)")
            if apt < 45.0:
                reasons.append(f"Critical aptitude gap ({apt}%)")
            if cod < 40.0:
                reasons.append(f"Low coding pass rate ({cod}%)")

            at_risk.append({
                "student_id": sp.id,
                "student_name": u.full_name,
                "overall_score": tot,
                "aptitude_score": apt,
                "coding_score": cod,
                "risk_factors": reasons,
            })

    at_risk.sort(key=lambda x: x["overall_score"])
    return {
        "count": len(at_risk),
        "at_risk_students": at_risk[:10],
    }


async def tool_get_coding_performance(
    ctx: TrainerContext, db: AsyncSession, batch_id: Optional[int] = None
) -> Dict[str, Any]:
    """Aggregates coding metrics across the trainer's cohort."""
    target_students = ctx.authorized_student_ids
    if batch_id is not None:
        if not ctx.is_batch_authorized(batch_id):
            return {"error": f"Access Denied: Batch {batch_id} is not authorized."}
        m_res = await db.execute(
            select(BatchMembership.student_id).where(BatchMembership.batch_id == batch_id, BatchMembership.is_active == True)
        )
        target_students = [row[0] for row in m_res.all()]

    if not target_students:
        return {"total_submissions": 0, "pass_rate": 0.0}

    sub_res = await db.execute(
        select(CodeSubmission).where(CodeSubmission.student_id.in_(target_students))
    )
    subs = sub_res.scalars().all()
    total = len(subs)
    accepted = sum(1 for s in subs if s.verdict == SubmissionVerdict.ACCEPTED)
    pass_rate = round((accepted / total * 100.0), 1) if total > 0 else 0.0

    lang_counts = {}
    verdict_counts = {}
    for s in subs:
        lang = s.language.lower() if s.language else "unknown"
        lang_counts[lang] = lang_counts.get(lang, 0) + 1
        v = s.verdict.value
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    return {
        "total_submissions": total,
        "accepted": accepted,
        "pass_rate": pass_rate,
        "language_distribution": lang_counts,
        "verdict_distribution": verdict_counts,
    }


async def tool_get_malpractice_summary(
    ctx: TrainerContext, db: AsyncSession, test_id: int
) -> Dict[str, Any]:
    """Retrieves proctoring malpractice audit log for an assessment."""
    t_res = await db.execute(select(Test).where(Test.id == test_id))
    test = t_res.scalar_one_or_none()
    if not test:
        return {"error": f"Test ID {test_id} not found."}
    if test.created_by != ctx.user_id:
        return {"error": f"Access Denied: Test ID {test_id} was not created by you."}

    att_res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.test_id == test_id)
        .options(
            selectinload(TestAttempt.proctoring_events),
            selectinload(TestAttempt.student).selectinload(StudentProfile.user),
        )
    )
    attempts = att_res.scalars().all()

    reports = []
    for a in attempts:
        risk = calculate_malpractice_risk(a.proctoring_events)
        name = a.student.user.full_name if a.student and a.student.user else f"Student {a.student_id}"
        reports.append({
            "student_id": a.student_id,
            "student_name": name,
            "score": a.score,
            "risk_level": risk["risk_level"],
            "total_violations": risk["total_violations"],
            "violation_breakdown": risk["event_counts"],
        })

    high_risk = [r for r in reports if r["risk_level"] == "HIGH"]
    return {
        "test_id": test_id,
        "test_title": test.title,
        "total_attempts": len(attempts),
        "high_risk_count": len(high_risk),
        "audit_reports": sorted(reports, key=lambda x: x["total_violations"], reverse=True)[:8],
    }


async def tool_get_anomaly_results(
    ctx: TrainerContext, db: AsyncSession, batch_id: Optional[int] = None
) -> Dict[str, Any]:
    """Runs Isolation Forest behavioral anomaly detection across assessments."""
    target_students = ctx.authorized_student_ids
    if not target_students:
        return {"status": "INSUFFICIENT_DATA", "message": "No students found in authorized cohort."}

    att_res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.student_id.in_(target_students))
        .options(
            selectinload(TestAttempt.proctoring_events),
            selectinload(TestAttempt.student).selectinload(StudentProfile.user),
        )
    )
    attempts = att_res.scalars().all()

    attempt_data = []
    for a in attempts:
        dur = int((a.submitted_at - a.started_at).total_seconds()) if (a.submitted_at and a.started_at) else 60
        dur = max(10, dur)
        attempt_data.append({
            "attempt_id": a.id,
            "student_id": a.student_id,
            "student_name": name,
            "duration_seconds": dur,
            "percentage": float(a.percentage or 0.0),
            "violation_count": len(a.proctoring_events),
            "submission_count": 1,
            "avg_time_per_question": max(5, int(dur / 5.0)),
        })

    return detect_assessment_anomalies(attempt_data)


# ─────────────────────────────────────────────────────────────────────────────
# Tool Definitions for LLM Function Calling
# ─────────────────────────────────────────────────────────────────────────────

AVAILABLE_TOOLS_SPEC = [
    {
        "name": "get_weak_students",
        "description": "Finds students whose accuracy or skill in a specific topic (e.g. Reasoning, Arrays, DP) is below 60%.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The topic name (e.g., 'Logical Reasoning', 'Arrays', 'Conditions')"},
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    },
    {
        "name": "get_batch_summary",
        "description": "Retrieves high-level performance metrics for a batch including student count, average aptitude, average coding, and at-risk counts.",
        "parameters": {
            "type": "object",
            "properties": {
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    },
    {
        "name": "get_student_performance",
        "description": "Retrieves comprehensive performance data for a single student by student ID (validates trainer authorization).",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer", "description": "The student profile ID"}
            },
            "required": ["student_id"]
        }
    },
    {
        "name": "get_placement_readiness",
        "description": "Determines which students are placement ready, developing, or need improvement using the XGBoost ML model.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer", "description": "Optional student profile ID"},
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    },
    {
        "name": "get_at_risk_students",
        "description": "Identifies candidates with low aggregate scores (<50%), critical aptitude gaps, or high risk.",
        "parameters": {
            "type": "object",
            "properties": {
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    },
    {
        "name": "get_coding_performance",
        "description": "Aggregates cohort algorithmic coding metrics, pass rates, language breakdown, and submission volumes.",
        "parameters": {
            "type": "object",
            "properties": {
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    },
    {
        "name": "get_malpractice_summary",
        "description": "Audits proctoring events and computes malpractice risk (tab switches, window blurs, full-screen exits) for a test.",
        "parameters": {
            "type": "object",
            "properties": {
                "test_id": {"type": "integer", "description": "Assessment test ID"}
            },
            "required": ["test_id"]
        }
    },
    {
        "name": "get_anomaly_results",
        "description": "Runs Isolation Forest behavioral anomaly detection to identify unusually fast completion velocities or score anomalies.",
        "parameters": {
            "type": "object",
            "properties": {
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    }
]

TOOL_DISPATCH = {
    "get_weak_students": tool_get_weak_students,
    "get_batch_summary": tool_get_batch_summary,
    "get_student_performance": tool_get_student_performance,
    "get_placement_readiness": tool_get_placement_readiness,
    "get_at_risk_students": tool_get_at_risk_students,
    "get_coding_performance": tool_get_coding_performance,
    "get_malpractice_summary": tool_get_malpractice_summary,
    "get_anomaly_results": tool_get_anomaly_results,
}
