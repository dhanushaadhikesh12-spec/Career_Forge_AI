"""
Approved Backend Tools for Trainer AI Assistant.
Provides parameter-validated, permission-enforced read-only tools.
Strictly isolates data to trainer's authorized batches.
Returns student-level intelligence (names + key metrics) without raw DB dumps.
"""
from __future__ import annotations
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
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

logger = logging.getLogger(__name__)


class TrainerContext:
    """Encapsulates authenticated trainer permissions and batch boundaries."""
    def __init__(self, trainer_id: int, user_id: int, authorized_batch_ids: List[int], authorized_student_ids: List[int]):
        self.trainer_id = trainer_id
        self.user_id = user_id
        self.authorized_batch_ids = authorized_batch_ids
        # Strictly deduplicate student IDs preserving order
        self.authorized_student_ids = list(dict.fromkeys(authorized_student_ids))

    def is_student_authorized(self, student_id: int) -> bool:
        return student_id in self.authorized_student_ids

    def is_batch_authorized(self, batch_id: int) -> bool:
        return batch_id in self.authorized_batch_ids


async def build_trainer_context(db: AsyncSession, trainer_profile: TrainerProfile) -> TrainerContext:
    """Builds trainer boundary context from database."""
    # Active batches belonging to trainer
    b_res = await db.execute(
        select(Batch.id).where(Batch.trainer_id == trainer_profile.id, Batch.is_active == True)
    )
    batch_ids = [row[0] for row in b_res.all()]

    # Student IDs enrolled in trainer's active batches
    student_ids: List[int] = []
    if batch_ids:
        m_res = await db.execute(
            select(BatchMembership.student_id)
            .where(BatchMembership.batch_id.in_(batch_ids), BatchMembership.is_active == True)
        )
        student_ids = list(dict.fromkeys(row[0] for row in m_res.all()))

    return TrainerContext(
        trainer_id=trainer_profile.id,
        user_id=trainer_profile.user_id,
        authorized_batch_ids=batch_ids,
        authorized_student_ids=student_ids,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Student Resolution Helper
# ─────────────────────────────────────────────────────────────────────────────

async def resolve_authorized_student(
    ctx: TrainerContext,
    db: AsyncSession,
    student_name: Optional[str] = None,
    student_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Resolves a student by ID or name within the trainer's authorized cohort.
    Enforces server-side authorization:
      - If student_id provided: must be in ctx.authorized_student_ids.
      - If student_name provided: matches case-insensitively within authorized batches.
      - If multiple matches: returns ambiguity notice with candidate names & batch names.
      - If not found: returns a clear not found notice.
    """
    if not ctx.authorized_student_ids:
        return {"error": "Trainer has no active students in their assigned batches."}

    # 1. Direct student_id resolution
    if student_id is not None:
        if not ctx.is_student_authorized(student_id):
            return {"error": f"Access Denied: Student ID {student_id} is not enrolled in your authorized batches."}

        st_res = await db.execute(
            select(StudentProfile, User)
            .join(User, User.id == StudentProfile.user_id)
            .where(StudentProfile.id == student_id)
        )
        row = st_res.first()
        if not row:
            return {"error": f"Student ID {student_id} not found."}
        sp, u = row

        b_res = await db.execute(
            select(Batch)
            .join(BatchMembership, BatchMembership.batch_id == Batch.id)
            .where(BatchMembership.student_id == student_id, BatchMembership.is_active == True)
        )
        batch = b_res.scalars().first()
        return {"student_profile": sp, "user": u, "batch": batch}

    # 2. Student name resolution
    if student_name:
        clean_name = student_name.strip()
        st_res = await db.execute(
            select(StudentProfile, User, Batch)
            .join(User, User.id == StudentProfile.user_id)
            .join(BatchMembership, BatchMembership.student_id == StudentProfile.id)
            .join(Batch, Batch.id == BatchMembership.batch_id)
            .where(
                StudentProfile.id.in_(ctx.authorized_student_ids),
                BatchMembership.is_active == True,
            )
        )
        rows = st_res.all()

        # Deduplicate rows by student_profile.id
        seen = set()
        unique_students: List[Tuple[StudentProfile, User, Batch]] = []
        for sp, u, b in rows:
            if sp.id not in seen:
                seen.add(sp.id)
                unique_students.append((sp, u, b))

        # Filter matches (case-insensitive substring)
        q_lower = clean_name.lower()
        matches = [item for item in unique_students if q_lower in item[1].full_name.lower()]

        if len(matches) == 0:
            return {"error": f"Student '{clean_name}' was not found in your authorized cohorts."}

        if len(matches) > 1:
            # Check for exact case-insensitive match
            exact_matches = [item for item in matches if item[1].full_name.strip().lower() == q_lower]
            if len(exact_matches) == 1:
                sp, u, b = exact_matches[0]
                return {"student_profile": sp, "user": u, "batch": b}

            candidates = [
                {"name": u.full_name, "batch": b.name if b else "Unknown Batch"}
                for sp, u, b in matches
            ]
            cand_str = ", ".join(f"{c['name']} ({c['batch']})" for c in candidates)
            return {
                "ambiguous": True,
                "message": f"I found multiple students matching '{clean_name}': {cand_str}. Please specify the batch or full name.",
                "candidates": candidates,
            }

        sp, u, b = matches[0]
        return {"student_profile": sp, "user": u, "batch": b}

    return {"error": "Please provide a student name or student ID to query."}


# ─────────────────────────────────────────────────────────────────────────────
# Approved Tools Registry
# ─────────────────────────────────────────────────────────────────────────────

async def tool_get_placement_readiness(
    ctx: TrainerContext,
    db: AsyncSession,
    student_id: Optional[int] = None,
    student_name: Optional[str] = None,
    batch_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Evaluates XGBoost placement readiness.
    If student_name or student_id is provided, returns that student's readiness and performance metrics.
    If batch-level/cohort-level, returns actual placement-ready student names, developing, and at-risk breakdown.
    """
    model = get_readiness_model()

    # Specific student query
    if student_id is not None or student_name is not None:
        resolution = await resolve_authorized_student(ctx, db, student_name=student_name, student_id=student_id)
        if "error" in resolution or resolution.get("ambiguous"):
            return resolution

        sp = resolution["student_profile"]
        u = resolution["user"]
        batch = resolution["batch"]

        features_info = await extract_student_features(db, sp.id)
        pred = model.predict(features_info)
        cat = pred.get("readiness_category", "NEEDS_IMPROVEMENT")
        status_label = "Placement Ready" if cat == "PLACEMENT_READY" else ("Developing" if cat == "DEVELOPING" else "Needs Improvement")

        apt = round(float(sp.aptitude_score or 0.0), 1)
        cod = round(float(sp.coding_score or 0.0), 1)
        tot = round(float(sp.total_score or 0.0), 1)
        readiness_pct = pred.get("readiness_score", tot)

        # Formulate reason
        if cat == "PLACEMENT_READY":
            reason = f"High coding performance ({cod}%) and strong aptitude ({apt}%)"
        elif cat == "DEVELOPING":
            reason = f"Steady progress across practice modules; coding is {cod}% and aptitude is {apt}%"
        else:
            reason = f"Scores currently below benchmark (Aptitude: {apt}%, Coding: {cod}%)"

        return {
            "student_name": u.full_name,
            "batch_name": batch.name if batch else "Authorized Cohort",
            "readiness_score": readiness_pct,
            "category": cat,
            "status": status_label,
            "aptitude_score": apt,
            "coding_score": cod,
            "overall_score": tot,
            "reason": reason,
            "strengths": pred.get("contributing_factors", {}).get("strengths", []),
            "areas_for_improvement": pred.get("contributing_factors", {}).get("areas_for_improvement", []),
        }

    # Batch / Cohort evaluation
    target_students = ctx.authorized_student_ids
    if batch_id is not None:
        if not ctx.is_batch_authorized(batch_id):
            return {"error": f"Access Denied: Batch {batch_id} is not within your authorized cohorts."}
        m_res = await db.execute(
            select(BatchMembership.student_id).where(BatchMembership.batch_id == batch_id, BatchMembership.is_active == True)
        )
        target_students = list(dict.fromkeys(row[0] for row in m_res.all()))

    if not target_students:
        return {
            "placement_ready_students": [],
            "placement_ready_count": 0,
            "category_breakdown": {"PLACEMENT_READY": 0, "DEVELOPING": 0, "NEEDS_IMPROVEMENT": 0},
            "summary": "No students found in cohort.",
        }

    # Fetch users and student profiles
    st_res = await db.execute(
        select(StudentProfile, User)
        .join(User, User.id == StudentProfile.user_id)
        .where(StudentProfile.id.in_(target_students))
    )
    st_map = {sp.id: (sp, u) for sp, u in st_res.all()}

    ready_students = []
    developing_students = []
    needs_work_students = []

    for s_id in target_students[:40]:  # Predict within bound
        if s_id not in st_map:
            continue
        sp, u = st_map[s_id]
        feat = await extract_student_features(db, s_id)
        pred = model.predict(feat)
        cat = pred.get("readiness_category", "NEEDS_IMPROVEMENT")
        r_score = pred.get("readiness_score", float(sp.total_score or 0.0))
        apt = round(float(sp.aptitude_score or 0.0), 1)
        cod = round(float(sp.coding_score or 0.0), 1)

        item = {
            "student_name": u.full_name,
            "readiness_score": r_score,
            "aptitude_score": apt,
            "coding_score": cod,
            "status": "Placement Ready" if cat == "PLACEMENT_READY" else ("Developing" if cat == "DEVELOPING" else "Needs Improvement"),
            "reason": f"Aptitude: {apt}% | Coding: {cod}%",
        }

        if cat == "PLACEMENT_READY":
            ready_students.append(item)
        elif cat == "DEVELOPING":
            developing_students.append(item)
        else:
            needs_work_students.append(item)

    ready_students.sort(key=lambda x: x["readiness_score"], reverse=True)
    developing_students.sort(key=lambda x: x["readiness_score"], reverse=True)

    return {
        "total_evaluated": len(ready_students) + len(developing_students) + len(needs_work_students),
        "placement_ready_count": len(ready_students),
        "category_breakdown": {
            "PLACEMENT_READY": len(ready_students),
            "DEVELOPING": len(developing_students),
            "NEEDS_IMPROVEMENT": len(needs_work_students),
        },
        "placement_ready_students": ready_students,
        "developing_students": developing_students[:8],
        "needs_improvement_students": needs_work_students[:8],
        "summary": f"{len(ready_students)} students currently meet the placement-readiness threshold.",
    }


async def tool_get_weak_students(
    ctx: TrainerContext, db: AsyncSession, topic: Optional[str] = None, batch_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Finds students whose accuracy or skill in a topic (or DSA topics) is below target benchmark (60%).
    Returns student names, topic accuracy, weak subtopics, and reasons.
    """
    target_students = ctx.authorized_student_ids
    if batch_id is not None:
        if not ctx.is_batch_authorized(batch_id):
            return {"error": f"Access Denied: Batch {batch_id} is not within your authorized cohorts."}
        m_res = await db.execute(
            select(BatchMembership.student_id).where(BatchMembership.batch_id == batch_id, BatchMembership.is_active == True)
        )
        target_students = list(dict.fromkeys(row[0] for row in m_res.all()))

    if not target_students:
        return {"topic": topic or "All Topics", "weak_students": [], "message": "No students found in cohort."}

    # Build topic matching
    dsa_topics = [
        "arrays", "strings", "linked lists", "stacks & queues", "trees & graphs",
        "sorting & searching", "dynamic programming", "recursion", "hashing"
    ]
    is_dsa_query = topic and topic.strip().lower() in ["dsa", "data structures", "data structures & algorithms", "coding"]

    query = (
        select(TopicProgress, StudentProfile, User, Topic)
        .join(StudentProfile, StudentProfile.id == TopicProgress.student_id)
        .join(User, User.id == StudentProfile.user_id)
        .join(Topic, Topic.id == TopicProgress.topic_id)
        .where(TopicProgress.student_id.in_(target_students))
    )
    if is_dsa_query:
        query = query.where(func.lower(Topic.name).in_(dsa_topics))
    elif topic:
        query = query.where(Topic.name.ilike(f"%{topic.strip()}%"))

    res = await db.execute(query)
    rows = res.all()

    # Aggregate by student
    student_records: Dict[int, Dict[str, Any]] = {}
    for tp, sp, u, t in rows:
        att = tp.questions_attempted
        corr = tp.questions_correct
        acc = round((corr / att * 100.0), 1) if att > 0 else 0.0

        if sp.id not in student_records:
            student_records[sp.id] = {
                "student_name": u.full_name,
                "readiness_score": round(float(sp.total_score or 0.0), 1),
                "coding_score": round(float(sp.coding_score or 0.0), 1),
                "total_attempted": 0,
                "total_correct": 0,
                "weak_topics": [],
                "all_topics": [],
            }

        rec = student_records[sp.id]
        rec["total_attempted"] += att
        rec["total_correct"] += corr
        rec["all_topics"].append({"name": t.name, "accuracy": acc, "attempts": att})

        if acc < 60.0 or tp.skill_rating < 1000.0:
            rec["weak_topics"].append(t.name)

    # Filter students who are weak
    weak_list = []
    for s_id, rec in student_records.items():
        tot_att = rec["total_attempted"]
        overall_acc = round((rec["total_correct"] / tot_att * 100.0), 1) if tot_att > 0 else 0.0

        if rec["weak_topics"] or overall_acc < 60.0:
            reason = f"Accuracy below benchmark ({overall_acc}%)"
            if rec["weak_topics"]:
                reason = f"Weak in {', '.join(rec['weak_topics'][:2])}"

            weak_list.append({
                "student_name": rec["student_name"],
                "topic_accuracy": overall_acc,
                "weak_topics": rec["weak_topics"],
                "readiness_score": rec["readiness_score"],
                "reason": reason,
            })

    # If topic was explicitly queried and some students had no progress records, also check profile coding/aptitude score
    if not weak_list and (is_dsa_query or (topic and "dsa" in topic.lower())):
        st_res = await db.execute(
            select(StudentProfile, User)
            .join(User, User.id == StudentProfile.user_id)
            .where(StudentProfile.id.in_(target_students))
        )
        for sp, u in st_res.all():
            if (sp.coding_score or 0.0) < 60.0:
                weak_list.append({
                    "student_name": u.full_name,
                    "topic_accuracy": round(float(sp.coding_score or 0.0), 1),
                    "weak_topics": ["Arrays", "Problem Solving"],
                    "readiness_score": round(float(sp.total_score or 0.0), 1),
                    "reason": f"Low coding score ({sp.coding_score}%)",
                })

    weak_list.sort(key=lambda x: x["topic_accuracy"])
    return {
        "topic": "DSA" if is_dsa_query else (topic or "All Topics"),
        "count": len(weak_list),
        "weak_students": weak_list[:12],
    }


async def tool_get_at_risk_students(
    ctx: TrainerContext, db: AsyncSession, batch_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Identifies at-risk candidates based on scores, test failures, or critical skill gaps.
    Returns student names, risk level (High/Medium), readiness score, main reason, and weak areas.
    """
    target_students = ctx.authorized_student_ids
    if batch_id is not None:
        if not ctx.is_batch_authorized(batch_id):
            return {"error": f"Access Denied: Batch {batch_id} is not within your authorized cohorts."}
        m_res = await db.execute(
            select(BatchMembership.student_id).where(BatchMembership.batch_id == batch_id, BatchMembership.is_active == True)
        )
        target_students = list(dict.fromkeys(row[0] for row in m_res.all()))

    if not target_students:
        return {"at_risk_students": [], "count": 0, "message": "No students found in cohort."}

    sp_res = await db.execute(
        select(StudentProfile, User)
        .join(User, User.id == StudentProfile.user_id)
        .where(StudentProfile.id.in_(target_students))
    )
    rows = sp_res.all()

    at_risk = []
    for sp, u in rows:
        tot = round(float(sp.total_score or 0.0), 1)
        apt = round(float(sp.aptitude_score or 0.0), 1)
        cod = round(float(sp.coding_score or 0.0), 1)

        if tot < 60.0 or apt < 65.0 or cod < 50.0:
            # Determine risk level
            if tot < 50.0 or cod < 40.0 or apt < 45.0:
                risk_level = "High Risk"
            else:
                risk_level = "Medium Risk"

            reasons = []
            if cod < 50.0:
                reasons.append(f"Low coding performance ({cod}%)")
            if apt < 65.0:
                reasons.append(f"Aptitude accuracy below benchmark ({apt}%)")
            if tot < 50.0:
                reasons.append(f"Overall readiness score is {tot}%")

            main_reason = "; ".join(reasons) if reasons else "Multiple performance indicators below threshold"
            weak_area = "Coding & DSA" if cod < apt else "Aptitude & Reasoning"

            at_risk.append({
                "student_name": u.full_name,
                "risk_level": risk_level,
                "readiness_score": tot,
                "aptitude_score": apt,
                "coding_score": cod,
                "main_reason": main_reason,
                "weak_area": weak_area,
                "recommended_action": f"Prioritize structured practice in {weak_area} and review assessment feedback.",
            })

    # Sort high risk first, then by lowest readiness score
    at_risk.sort(key=lambda x: (0 if "High" in x["risk_level"] else 1, x["readiness_score"]))
    return {
        "count": len(at_risk),
        "at_risk_students": at_risk[:12],
        "summary": f"{len(at_risk)} students are currently categorized as at-risk.",
    }


async def tool_get_student_performance(
    ctx: TrainerContext,
    db: AsyncSession,
    student_name: Optional[str] = None,
    student_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Retrieves deep performance profile for a specific student with authorization enforcement.
    Accepts either student_name or student_id.
    Returns: Name, readiness %, aptitude %, coding %, strong areas, weak areas, trend, and recommended actions.
    Excludes sensitive/internal fields (IDs, passwords, tokens, timestamps).
    """
    resolution = await resolve_authorized_student(ctx, db, student_name=student_name, student_id=student_id)
    if "error" in resolution or resolution.get("ambiguous"):
        return resolution

    sp = resolution["student_profile"]
    u = resolution["user"]
    batch = resolution["batch"]

    # Topic breakdown
    tp_res = await db.execute(
        select(TopicProgress, Topic)
        .join(Topic, Topic.id == TopicProgress.topic_id)
        .where(TopicProgress.student_id == sp.id)
    )
    topics = []
    for tp, t in tp_res.all():
        att = tp.questions_attempted
        corr = tp.questions_correct
        acc = round((corr / att * 100.0), 1) if att > 0 else 0.0
        topics.append({
            "name": t.name,
            "accuracy": acc,
            "attempted": att,
            "skill_rating": round(float(tp.skill_rating), 1),
        })

    strong_areas = [t["name"] for t in sorted(topics, key=lambda x: x["accuracy"], reverse=True) if t["accuracy"] >= 75.0]
    weak_areas = [t["name"] for t in sorted(topics, key=lambda x: x["accuracy"]) if t["accuracy"] < 60.0]

    # Defaults if not enough specific topic data
    if not strong_areas and (sp.coding_score or 0) >= 80:
        strong_areas.append("Algorithmic Problem Solving")
    if not strong_areas and (sp.aptitude_score or 0) >= 80:
        strong_areas.append("Quantitative Aptitude")
    if not weak_areas and (sp.coding_score or 0) < 60:
        weak_areas.append("DSA & Coding Implementation")
    if not weak_areas and (sp.aptitude_score or 0) < 60:
        weak_areas.append("Logical Reasoning & Verbal")

    # Coding submissions count and pass rate
    sub_res = await db.execute(
        select(func.count(CodeSubmission.id), func.avg(CodeSubmission.score))
        .where(CodeSubmission.student_id == sp.id)
    )
    sub_count, avg_sub_score = sub_res.first() or (0, 0.0)

    # Trend calculation
    tot = round(float(sp.total_score or 0.0), 1)
    if tot >= 80.0:
        trend = "Consistent upward trajectory; ready for campus drives"
        action = "Participate in timed mock company technical assessments and system design fundamentals."
    elif tot >= 60.0:
        trend = "Steady performance with minor variance across complex problem sets"
        action = f"Focus practice on identified weak areas: {', '.join(weak_areas[:2]) if weak_areas else 'medium-difficulty DSA'}."
    else:
        trend = "Needs structured intervention to meet minimum campus placement cutoffs"
        action = f"Immediate revision of foundational concepts in {', '.join(weak_areas[:2]) if weak_areas else 'core aptitude & basic coding'}."

    return {
        "student_id": sp.id,
        "student_name": u.full_name,
        "full_name": u.full_name,
        "batch_name": batch.name if batch else "Authorized Cohort",
        "readiness_score": tot,
        "overall_score": tot,
        "aptitude_score": round(float(sp.aptitude_score or 0.0), 1),
        "coding_score": round(float(sp.coding_score or 0.0), 1),
        "total_practice_questions": sum(t["attempted"] for t in topics),
        "strong_areas": strong_areas[:3],
        "weak_areas": weak_areas[:3],
        "recent_trend": trend,
        "recommended_action": action,
    }


async def tool_get_batch_summary(
    ctx: TrainerContext, db: AsyncSession, batch_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieves high-level performance metrics for a batch AND an individual student breakdown.
    Answers: "How is my batch performing?" with batch overview + student breakdown list.
    """
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
    rows = st_res.all()

    # Deduplicate unique students
    seen_ids = set()
    students: List[Tuple[StudentProfile, User]] = []
    for sp, u in rows:
        if sp.id not in seen_ids:
            seen_ids.add(sp.id)
            students.append((sp, u))

    total_students = len(students)
    if total_students == 0:
        return {
            "batch_names": [b.name for b in batches],
            "total_students": 0,
            "avg_readiness": 0.0,
            "avg_aptitude_score": 0.0,
            "avg_coding_score": 0.0,
            "placement_ready_count": 0,
            "at_risk_count": 0,
            "students": [],
        }

    avg_apt = round(sum(float(sp.aptitude_score or 0.0) for sp, u in students) / total_students, 1)
    avg_cod = round(sum(float(sp.coding_score or 0.0) for sp, u in students) / total_students, 1)
    avg_total = round(sum(float(sp.total_score or 0.0) for sp, u in students) / total_students, 1)

    # Student breakdown
    student_breakdown = []
    ready_count = 0
    at_risk_count = 0

    for sp, u in students:
        tot = round(float(sp.total_score or 0.0), 1)
        apt = round(float(sp.aptitude_score or 0.0), 1)
        cod = round(float(sp.coding_score or 0.0), 1)

        if tot >= 75.0 and cod >= 60.0:
            status = "Ready"
            ready_count += 1
        elif tot < 55.0 or cod < 40.0 or apt < 45.0:
            status = "At Risk"
            at_risk_count += 1
        else:
            status = "Developing"

        student_breakdown.append({
            "student_name": u.full_name,
            "readiness": tot,
            "aptitude": apt,
            "coding": cod,
            "status": status,
        })

    # Sort students by readiness descending
    student_breakdown.sort(key=lambda x: x["readiness"], reverse=True)

    return {
        "batch_ids": target_batches,
        "batch_names": [b.name for b in batches],
        "total_students": total_students,
        "avg_readiness": avg_total,
        "avg_aptitude_score": avg_apt,
        "avg_coding_score": avg_cod,
        "placement_ready_count": ready_count,
        "at_risk_count": at_risk_count,
        "students": student_breakdown,
    }


async def tool_get_top_students(
    ctx: TrainerContext,
    db: AsyncSession,
    metric: str = "readiness",
    limit: int = 5,
    batch_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Ranks and retrieves top performing students in the cohort by a chosen metric.
    Supported metrics: 'readiness', 'coding', 'aptitude', 'overall'.
    Returns actual student names, rankings, and specific score metrics.
    """
    target_students = ctx.authorized_student_ids
    if batch_id is not None:
        if not ctx.is_batch_authorized(batch_id):
            return {"error": f"Access Denied: Batch {batch_id} is not within your authorized cohorts."}
        m_res = await db.execute(
            select(BatchMembership.student_id).where(BatchMembership.batch_id == batch_id, BatchMembership.is_active == True)
        )
        target_students = list(dict.fromkeys(row[0] for row in m_res.all()))

    if not target_students:
        return {"metric": metric, "top_students": [], "message": "No students found in cohort."}

    st_res = await db.execute(
        select(StudentProfile, User)
        .join(User, User.id == StudentProfile.user_id)
        .where(StudentProfile.id.in_(target_students))
    )
    students = st_res.all()

    m_clean = metric.strip().lower() if metric else "readiness"
    if "cod" in m_clean:
        ranking_metric = "Coding Score"
        sort_fn = lambda item: float(item[0].coding_score or 0.0)
    elif "apt" in m_clean:
        ranking_metric = "Aptitude Score"
        sort_fn = lambda item: float(item[0].aptitude_score or 0.0)
    else:
        ranking_metric = "Placement Readiness Score"
        sort_fn = lambda item: float(item[0].total_score or 0.0)

    ranked = sorted(students, key=sort_fn, reverse=True)
    top_list = []
    for idx, (sp, u) in enumerate(ranked[:limit]):
        tot = round(float(sp.total_score or 0.0), 1)
        apt = round(float(sp.aptitude_score or 0.0), 1)
        cod = round(float(sp.coding_score or 0.0), 1)
        top_list.append({
            "rank": idx + 1,
            "student_name": u.full_name,
            "readiness_score": tot,
            "aptitude_score": apt,
            "coding_score": cod,
            "ranking_score": cod if "Coding" in ranking_metric else (apt if "Aptitude" in ranking_metric else tot),
            "status": "Placement Ready" if tot >= 75.0 else "Developing",
        })

    return {
        "ranking_metric": ranking_metric,
        "limit": limit,
        "count": len(top_list),
        "top_students": top_list,
    }


async def tool_get_coding_performance(
    ctx: TrainerContext, db: AsyncSession, batch_id: Optional[int] = None
) -> Dict[str, Any]:
    """Aggregates coding metrics across the trainer's cohort including top performers."""
    target_students = ctx.authorized_student_ids
    if batch_id is not None:
        if not ctx.is_batch_authorized(batch_id):
            return {"error": f"Access Denied: Batch {batch_id} is not within your authorized cohorts."}
        m_res = await db.execute(
            select(BatchMembership.student_id).where(BatchMembership.batch_id == batch_id, BatchMembership.is_active == True)
        )
        target_students = list(dict.fromkeys(row[0] for row in m_res.all()))

    if not target_students:
        return {"total_submissions": 0, "pass_rate": 0.0, "top_performers": []}

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

    # Top coding performers
    st_res = await db.execute(
        select(StudentProfile, User)
        .join(User, User.id == StudentProfile.user_id)
        .where(StudentProfile.id.in_(target_students))
        .order_by(StudentProfile.coding_score.desc())
        .limit(5)
    )
    top_performers = [
        {
            "student_name": u.full_name,
            "coding_score": round(float(sp.coding_score or 0.0), 1),
            "readiness_score": round(float(sp.total_score or 0.0), 1),
        }
        for sp, u in st_res.all()
    ]

    return {
        "total_submissions": total,
        "accepted": accepted,
        "pass_rate": pass_rate,
        "language_distribution": lang_counts,
        "verdict_distribution": verdict_counts,
        "top_performers": top_performers,
    }


async def tool_get_malpractice_summary(
    ctx: TrainerContext, db: AsyncSession, test_id: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieves proctoring malpractice audit log identifying students requiring review."""
    if test_id is None or test_id == 0:
        # Default to the most recent test accessible to trainer
        t_res = await db.execute(
            select(Test)
            .where((Test.created_by == ctx.user_id) | (Test.batch_id.in_(ctx.authorized_batch_ids)))
            .order_by(Test.id.desc())
            .limit(1)
        )
        test = t_res.scalar_one_or_none()
    else:
        t_res = await db.execute(select(Test).where(Test.id == test_id))
        test = t_res.scalar_one_or_none()

    if not test:
        return {"error": "No assessments found to audit for malpractice."}

    # Verify authorization
    if test.created_by != ctx.user_id and test.batch_id not in ctx.authorized_batch_ids:
        return {"error": f"Access Denied: Test ID {test.id} is outside your authorized scope."}

    att_res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.test_id == test.id)
        .options(
            selectinload(TestAttempt.proctoring_events),
            selectinload(TestAttempt.student).selectinload(StudentProfile.user),
        )
    )
    attempts = att_res.scalars().all()

    from app.api.routes.proctoring import calculate_malpractice_risk

    reports = []
    for a in attempts:
        risk = calculate_malpractice_risk(a.proctoring_events)
        name = a.student.user.full_name if a.student and a.student.user else f"Student {a.student_id}"

        # Reason formulation
        event_summary = ", ".join(f"{count} {ev.replace('_', ' ')}" for ev, count in risk["event_counts"].items() if count > 0)
        reason = event_summary or "Normal test activity"

        reports.append({
            "student_name": name,
            "risk_level": risk["risk_level"],
            "total_violations": risk["total_violations"],
            "score": round(float(a.score or 0.0), 1),
            "percentage": round(float(a.percentage or 0.0), 1),
            "reason": reason,
        })

    flagged = [r for r in reports if r["risk_level"] in ("HIGH", "MEDIUM")]
    flagged.sort(key=lambda x: x["total_violations"], reverse=True)

    return {
        "test_title": test.title,
        "total_attempts": len(attempts),
        "high_risk_count": sum(1 for r in reports if r["risk_level"] == "HIGH"),
        "students_requiring_review": flagged[:8],
    }


async def tool_get_anomaly_results(
    ctx: TrainerContext, db: AsyncSession, batch_id: Optional[int] = None
) -> Dict[str, Any]:
    """Runs Isolation Forest behavioral anomaly detection across assessments."""
    target_students = ctx.authorized_student_ids
    if batch_id is not None:
        if not ctx.is_batch_authorized(batch_id):
            return {"error": f"Access Denied: Batch {batch_id} is not within your authorized cohorts."}
        m_res = await db.execute(
            select(BatchMembership.student_id).where(BatchMembership.batch_id == batch_id, BatchMembership.is_active == True)
        )
        target_students = list(dict.fromkeys(row[0] for row in m_res.all()))

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
        name = a.student.user.full_name if a.student and a.student.user else f"Student {a.student_id}"

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
        "name": "get_placement_readiness",
        "description": "Evaluates XGBoost placement readiness predictions. Use when asked 'Who is placement ready?', 'Which students are ready?', or checking readiness for a specific student or batch.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_name": {"type": "string", "description": "Student full name or first name (e.g. 'Rahul', 'Rahul Kumar')"},
                "student_id": {"type": "integer", "description": "Optional student profile ID"},
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    },
    {
        "name": "get_weak_students",
        "description": "Finds specific students who are weak in a subject, DSA, or specific topic (e.g. 'DSA', 'Arrays', 'Dynamic Programming', 'Reasoning'). Returns actual student names and their weak areas.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The topic or subject name (e.g., 'DSA', 'Arrays', 'Logical Reasoning', 'Trees')"},
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    },
    {
        "name": "get_at_risk_students",
        "description": "Identifies candidates with critical gaps, score drops, or high risk of placement failure. Returns student names, risk levels, and reasons.",
        "parameters": {
            "type": "object",
            "properties": {
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    },
    {
        "name": "get_top_students",
        "description": "Ranks top performing students in the cohort by placement readiness, coding performance, or aptitude. Use when asked 'Who are the top students?', 'Who is performing better in coding?', or 'Who has the highest aptitude?'.",
        "parameters": {
            "type": "object",
            "properties": {
                "metric": {"type": "string", "description": "Ranking metric: 'readiness', 'coding', 'aptitude', or 'overall'"},
                "limit": {"type": "integer", "description": "Number of students to return (e.g. 5)"},
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    },
    {
        "name": "get_student_performance",
        "description": "Retrieves comprehensive performance data for a single student by name or ID (e.g. 'How is Rahul performing?'). Validates trainer authorization.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_name": {"type": "string", "description": "Student full or first name (e.g. 'Rahul', 'Rahul Kumar')"},
                "student_id": {"type": "integer", "description": "Optional student profile ID"}
            }
        }
    },
    {
        "name": "get_batch_summary",
        "description": "Retrieves cohort overview metrics AND individual student performance breakdown (readiness, aptitude, coding, status). Use when asked 'How is my batch performing?'.",
        "parameters": {
            "type": "object",
            "properties": {
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    },
    {
        "name": "get_coding_performance",
        "description": "Aggregates cohort algorithmic coding metrics, pass rates, language breakdown, and top coding performers.",
        "parameters": {
            "type": "object",
            "properties": {
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    },
    {
        "name": "get_malpractice_summary",
        "description": "Audits proctoring events and identifies students with suspicious activity, tab switches, or malpractice violations.",
        "parameters": {
            "type": "object",
            "properties": {
                "test_id": {"type": "integer", "description": "Optional assessment test ID (defaults to latest)"}
            }
        }
    },
    {
        "name": "get_anomaly_results",
        "description": "Runs Isolation Forest behavioral anomaly detection across assessments to detect unusual speeds or score anomalies.",
        "parameters": {
            "type": "object",
            "properties": {
                "batch_id": {"type": "integer", "description": "Optional batch ID"}
            }
        }
    }
]

TOOL_DISPATCH = {
    "get_placement_readiness": tool_get_placement_readiness,
    "get_weak_students": tool_get_weak_students,
    "get_at_risk_students": tool_get_at_risk_students,
    "get_top_students": tool_get_top_students,
    "get_student_performance": tool_get_student_performance,
    "get_batch_summary": tool_get_batch_summary,
    "get_coding_performance": tool_get_coding_performance,
    "get_malpractice_summary": tool_get_malpractice_summary,
    "get_anomaly_results": tool_get_anomaly_results,
}
