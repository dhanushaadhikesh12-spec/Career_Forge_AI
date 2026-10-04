"""
Unified Student Scoring Engine for CareerForge AI.

Implements mathematically sound, responsive algorithms for:
- Aptitude Mastery (40% Practice Accuracy + 60% Assessment Performance)
- Coding Score (40% Problem Solving Practice + 60% Assessment Performance)
- Overall Score (Balanced composite)
- Total Completed Tests Count

Ensures metrics never freeze, never get stuck at hardcoded 100%, and update
dynamically across test submissions, practice sessions, and coding evaluations.
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
import logging

from app.models.user import StudentProfile
from app.models.content import PracticeAttempt
from app.models.test import Test, TestAttempt, AttemptStatus, TestType
from app.models.coding import CodeSubmission, SubmissionVerdict

logger = logging.getLogger(__name__)


async def calculate_student_scores(db: AsyncSession, student_id: int) -> Dict[str, Any]:
    """
    Computes dynamic scoring metrics for a student:
    - aptitude_score (0.0 to 100.0)
    - coding_score (0.0 to 100.0)
    - total_score (0.0 to 100.0)
    - practice_count (int)
    - tests_taken (int)
    - practice_accuracy (float)
    - unique_coding_solved (int)
    """
    # ──────────────── 1. Aptitude Practice Stats ────────────────
    prac_stats = await db.execute(
        select(
            func.count(PracticeAttempt.id),
            func.coalesce(func.sum(case((PracticeAttempt.is_correct == True, 1), else_=0)), 0),
        ).where(PracticeAttempt.student_id == student_id)
    )
    total_prac, correct_prac = prac_stats.one()
    total_prac = total_prac or 0
    correct_prac = correct_prac or 0
    practice_accuracy = (float(correct_prac) / float(total_prac) * 100.0) if total_prac > 0 else None

    # ──────────────── 2. Aptitude Assessments ────────────────
    apt_query = (
        select(TestAttempt)
        .join(Test, TestAttempt.test_id == Test.id)
        .where(TestAttempt.student_id == student_id)
        .where(Test.test_type == TestType.APTITUDE)
        .where(TestAttempt.status == AttemptStatus.GRADED)
        .where(TestAttempt.percentage != None)
        .order_by(TestAttempt.submitted_at.desc().nullslast(), TestAttempt.id.desc())
    )
    all_apt_attempts = (await db.execute(apt_query)).scalars().all()

    # Prioritize legitimate mock tests (max_score >= 5.0) if available to avoid unit test artifacts
    has_real_apt = any(a.max_score and a.max_score >= 5.0 for a in all_apt_attempts)
    valid_apt = [
        a for a in all_apt_attempts
        if (not has_real_apt) or (a.max_score and a.max_score >= 5.0)
    ]
    # Prefer attempts with active student score; fallback to all valid attempts
    active_apt = [a for a in valid_apt if (a.score or 0.0) > 0.0]
    eval_apt = active_apt[:3] if active_apt else valid_apt[:3]

    if eval_apt:
        apt_test_avg = sum(float(a.percentage or 0.0) for a in eval_apt) / float(len(eval_apt))
    else:
        apt_test_avg = None

    # Aptitude Mastery formula: 40% Practice Accuracy + 60% Mock Test Average
    if practice_accuracy is not None and apt_test_avg is not None:
        aptitude_score = round(0.4 * practice_accuracy + 0.6 * apt_test_avg, 1)
    elif practice_accuracy is not None:
        aptitude_score = round(practice_accuracy, 1)
    elif apt_test_avg is not None:
        aptitude_score = round(apt_test_avg, 1)
    else:
        aptitude_score = 0.0
    aptitude_score = min(100.0, max(0.0, aptitude_score))

    # ──────────────── 3. Coding Problem Solving Practice ────────────────
    solved_res = await db.execute(
        select(func.count(func.distinct(CodeSubmission.coding_question_id)))
        .where(CodeSubmission.student_id == student_id)
        .where(CodeSubmission.verdict == SubmissionVerdict.ACCEPTED)
    )
    unique_solved = solved_res.scalar() or 0
    # Practice milestone target: 20 problems = 100% practice capability
    coding_practice_score = min(100.0, unique_solved * 5.0)

    # ──────────────── 4. Coding Assessments ────────────────
    cod_query = (
        select(TestAttempt)
        .join(Test, TestAttempt.test_id == Test.id)
        .where(TestAttempt.student_id == student_id)
        .where(Test.test_type == TestType.CODING)
        .where(TestAttempt.status == AttemptStatus.GRADED)
        .where(TestAttempt.percentage != None)
        .order_by(TestAttempt.submitted_at.desc().nullslast(), TestAttempt.id.desc())
    )
    all_cod_attempts = (await db.execute(cod_query)).scalars().all()

    # Prioritize full assessments (max_score >= 10.0) over obsolete legacy tests if present
    has_full_cod = any(a.max_score and a.max_score >= 10.0 for a in all_cod_attempts)
    valid_cod = [
        a for a in all_cod_attempts
        if (not has_full_cod) or (a.max_score and a.max_score >= 10.0)
    ]
    # Prefer attempts with active student score; fallback to all valid attempts
    active_cod = [a for a in valid_cod if (a.score or 0.0) > 0.0]
    eval_cod = active_cod[:3] if active_cod else valid_cod[:3]

    if eval_cod:
        cod_test_avg = sum(float(a.percentage or 0.0) for a in eval_cod) / float(len(eval_cod))
    else:
        cod_test_avg = None

    # Coding Score formula: 60% Assessment Performance + 40% Problem Solving Practice
    if cod_test_avg is not None and unique_solved > 0:
        coding_score = round(0.6 * cod_test_avg + 0.4 * coding_practice_score, 1)
    elif cod_test_avg is not None:
        coding_score = round(cod_test_avg, 1)
    elif unique_solved > 0:
        coding_score = round(coding_practice_score, 1)
    else:
        coding_score = 0.0
    coding_score = min(100.0, max(0.0, coding_score))

    # ──────────────── 5. Overall Score Composite ────────────────
    if aptitude_score > 0.0 and coding_score > 0.0:
        total_score = round(0.5 * aptitude_score + 0.5 * coding_score, 1)
    elif aptitude_score > 0.0:
        total_score = aptitude_score
    elif coding_score > 0.0:
        total_score = coding_score
    else:
        total_score = 0.0
    total_score = min(100.0, max(0.0, total_score))

    # ──────────────── 6. Total Completed Tests Count ────────────────
    tt_result = await db.execute(
        select(func.count(TestAttempt.id))
        .where(TestAttempt.student_id == student_id)
        .where(TestAttempt.status.in_([AttemptStatus.GRADED, AttemptStatus.TIMED_OUT]))
    )
    tests_taken = tt_result.scalar() or 0

    return {
        "aptitude_score": aptitude_score,
        "coding_score": coding_score,
        "total_score": total_score,
        "practice_count": total_prac,
        "tests_taken": tests_taken,
        "practice_accuracy": round(practice_accuracy, 1) if practice_accuracy is not None else 0.0,
        "unique_coding_solved": unique_solved,
    }


async def calculate_and_sync_student_scores(db: AsyncSession, profile: StudentProfile) -> Dict[str, Any]:
    """
    Authoritative method to compute student metrics and synchronize profile in database.
    """
    metrics = await calculate_student_scores(db, profile.id)

    profile.aptitude_score = metrics["aptitude_score"]
    profile.coding_score = metrics["coding_score"]
    profile.total_score = metrics["total_score"]

    await db.commit()
    return metrics
