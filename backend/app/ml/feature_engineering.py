"""
Feature engineering module for student placement readiness prediction.
Extracts normalized multi-dimensional performance features from PostgreSQL.
"""
from __future__ import annotations
import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import StudentProfile, TopicProgress
from app.models.test import TestAttempt, AttemptStatus
from app.models.coding import CodeSubmission, SubmissionVerdict

logger = logging.getLogger(__name__)

FEATURE_NAMES = [
    "aptitude_accuracy",
    "topic_mastery",
    "coding_score",
    "assessment_score",
    "coding_problem_solving_rate",
    "improvement_trend",
    "test_completion_rate",
    "avg_response_time",
    "practice_frequency",
    "difficulty_performance",
]


async def extract_student_features(db: AsyncSession, student_id: int) -> Dict[str, Any]:
    """
    Extracts all 10 tabular ML features for a single student.
    Returns:
    {
        "student_id": int,
        "features": Dict[str, float],
        "feature_vector": List[float],
        "data_points_count": int,
        "has_sufficient_data": bool
    }
    """
    # 1. Student profile
    prof_res = await db.execute(
        select(StudentProfile).where(StudentProfile.id == student_id)
    )
    profile = prof_res.scalar_one_or_none()
    if not profile:
        return {
            "student_id": student_id,
            "features": {f: 0.0 for f in FEATURE_NAMES},
            "feature_vector": [0.0] * len(FEATURE_NAMES),
            "data_points_count": 0,
            "has_sufficient_data": False,
        }

    # 2. Topic Progress (aptitude practice & skill ratings)
    tp_res = await db.execute(
        select(TopicProgress).where(TopicProgress.student_id == student_id)
    )
    topics = tp_res.scalars().all()

    total_attempted = sum(t.questions_attempted for t in topics)
    total_correct = sum(t.questions_correct for t in topics)
    aptitude_accuracy = (
        round((total_correct / total_attempted) * 100.0, 1)
        if total_attempted > 0
        else float(profile.aptitude_score or 0.0)
    )

    avg_skill = (
        sum(float(t.skill_rating) for t in topics) / len(topics)
        if topics
        else 1000.0
    )
    # Normalize skill rating: 800 -> 0%, 1500 -> 100%
    topic_mastery = round(max(0.0, min(100.0, (avg_skill - 800.0) / 7.0)), 1)

    # 3. Graded Test Attempts
    att_res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.student_id == student_id)
        .order_by(TestAttempt.started_at.asc())
    )
    attempts = att_res.scalars().all()
    graded_attempts = [a for a in attempts if a.status == AttemptStatus.GRADED]

    if graded_attempts:
        assessment_score = round(
            sum(float(a.percentage or 0.0) for a in graded_attempts) / len(graded_attempts),
            1,
        )
        total_time = 0.0
        for a in graded_attempts:
            if a.submitted_at and a.started_at:
                dur = (a.submitted_at - a.started_at).total_seconds()
                total_time += max(10.0, dur)
            else:
                total_time += 60.0
        avg_resp_time = round(min(180.0, max(10.0, total_time / max(1, len(graded_attempts)))), 1)
        completion_rate = round(
            (len(graded_attempts) / max(1, len(attempts))) * 100.0, 1
        )
        # Trend: compare latest attempts to earlier ones
        if len(graded_attempts) >= 2:
            mid = len(graded_attempts) // 2
            first_half = graded_attempts[:mid]
            second_half = graded_attempts[mid:]
            avg_early = sum(float(a.percentage or 0.0) for a in first_half) / len(first_half)
            avg_late = sum(float(a.percentage or 0.0) for a in second_half) / len(second_half)
            improvement_trend = round(max(-50.0, min(50.0, avg_late - avg_early)), 1)
        else:
            improvement_trend = 0.0
    else:
        assessment_score = float(profile.total_score or 0.0)
        avg_resp_time = 45.0
        completion_rate = 100.0 if profile.total_score > 0 else 0.0
        improvement_trend = 0.0

    # 4. Coding Submissions
    sub_res = await db.execute(
        select(CodeSubmission).where(CodeSubmission.student_id == student_id)
    )
    submissions = sub_res.scalars().all()

    distinct_attempted_q = set(s.coding_question_id for s in submissions)
    distinct_solved_q = set(
        s.coding_question_id for s in submissions if s.verdict == SubmissionVerdict.ACCEPTED
    )

    coding_problem_solving_rate = (
        round((len(distinct_solved_q) / max(1, len(distinct_attempted_q))) * 100.0, 1)
        if distinct_attempted_q
        else 0.0
    )

    if submissions:
        coding_score = round(
            sum(float(s.score or 0.0) for s in submissions) / len(submissions), 1
        )
    else:
        coding_score = float(profile.coding_score or 0.0)

    practice_frequency = total_attempted + len(submissions) + len(attempts)

    # 5. Difficulty performance
    # Weighted composite of harder question mastery vs baseline
    diff_perf = round(
        max(
            0.0,
            min(
                100.0,
                (aptitude_accuracy * 0.4)
                + (coding_score * 0.4)
                + (topic_mastery * 0.2),
            ),
        ),
        1,
    )

    feature_map = {
        "aptitude_accuracy": float(aptitude_accuracy),
        "topic_mastery": float(topic_mastery),
        "coding_score": float(coding_score),
        "assessment_score": float(assessment_score),
        "coding_problem_solving_rate": float(coding_problem_solving_rate),
        "improvement_trend": float(improvement_trend),
        "test_completion_rate": float(completion_rate),
        "avg_response_time": float(avg_resp_time),
        "practice_frequency": float(practice_frequency),
        "difficulty_performance": float(diff_perf),
    }

    feature_vector = [feature_map[fn] for fn in FEATURE_NAMES]
    data_points = total_attempted + len(submissions) + len(attempts)
    has_sufficient = data_points >= 2 or profile.total_score > 0

    return {
        "student_id": student_id,
        "features": feature_map,
        "feature_vector": feature_vector,
        "data_points_count": data_points,
        "has_sufficient_data": has_sufficient,
    }
