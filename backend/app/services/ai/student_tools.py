"""
Student AI Personal Placement Coach — Authorized Backend Tools.
All tools strictly operate on the authenticated student's profile.
Never accepts student_id from LLM arguments, frontend, or chat.
Integrates with existing ML readiness, AdaptiveEngine, and PostgreSQL tables.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.user import StudentProfile, TopicProgress, User
from app.models.content import (
    Topic, Subject, SubjectCategory, Question, QuestionOption,
    PracticeAttempt, StudentQuestionHistory, LessonCompletion, Lesson
)
from app.models.test import (
    Test, TestAttempt, TestAnswer, TestQuestion, AttemptStatus, TestType
)
from app.models.coding import (
    CodingQuestion, CodeSubmission, SubmissionVerdict
)
from app.services.scoring import calculate_and_sync_student_scores
from app.services.adaptive_engine import AdaptiveEngine
from app.ml.feature_engineering import extract_student_features
from app.ml.readiness_model import get_readiness_model

logger = logging.getLogger(__name__)


def now_utc():
    return datetime.now(timezone.utc)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Assessment Safety Check
# ─────────────────────────────────────────────────────────────────────────────

async def get_active_assessment(
    student_profile: StudentProfile, db: AsyncSession
) -> Optional[Dict[str, Any]]:
    """
    Checks if the student has any active assessment currently in progress.
    """
    now = now_utc()
    stmt = (
        select(TestAttempt)
        .where(
            TestAttempt.student_id == student_profile.id,
            TestAttempt.status == AttemptStatus.IN_PROGRESS,
        )
        .options(selectinload(TestAttempt.test))
        .order_by(TestAttempt.started_at.desc())
        .limit(1)
    )
    res = await db.execute(stmt)
    attempt = res.scalar_one_or_none()
    if not attempt:
        return None

    # Check expiration
    if attempt.expires_at and attempt.expires_at < now:
        return None

    return {
        "attempt_id": attempt.id,
        "test_id": attempt.test_id,
        "test_title": attempt.test.title if attempt.test else "Assessment",
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "expires_at": attempt.expires_at.isoformat() if attempt.expires_at else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. Performance Tools
# ─────────────────────────────────────────────────────────────────────────────

async def _get_student_name(student_profile: StudentProfile, db: AsyncSession) -> str:
    """Async-safe helper to fetch student full name avoiding lazy load errors."""
    if "user" in student_profile.__dict__ and student_profile.user:
        return student_profile.user.full_name
    u_res = await db.execute(select(User.full_name).where(User.id == student_profile.user_id))
    name = u_res.scalar_one_or_none()
    return name or "Candidate"


async def get_my_performance(
    student_profile: StudentProfile, db: AsyncSession
) -> Dict[str, Any]:
    """
    Returns authenticated student's overall performance metrics.
    Uses authoritative scoring sync.
    """
    metrics = await calculate_and_sync_student_scores(db, student_profile)

    # Count tests completed
    att_res = await db.execute(
        select(func.count(TestAttempt.id))
        .where(
            TestAttempt.student_id == student_profile.id,
            TestAttempt.status == AttemptStatus.GRADED,
        )
    )
    tests_completed = att_res.scalar() or 0

    # Count practice attempts
    prac_res = await db.execute(
        select(func.count(PracticeAttempt.id))
        .where(PracticeAttempt.student_id == student_profile.id)
    )
    practice_count = prac_res.scalar() or 0

    student_name = await _get_student_name(student_profile, db)

    return {
        "student_name": student_name,
        "readiness_score": round(metrics.get("total_score", 0.0), 1),
        "aptitude_accuracy": round(metrics.get("aptitude_score", 0.0), 1),
        "coding_accuracy": round(metrics.get("coding_score", 0.0), 1),
        "tests_completed": tests_completed,
        "practice_attempts": practice_count,
        "streak_days": student_profile.streak_days or 0,
        "has_data": (tests_completed > 0 or practice_count > 0),
    }


async def get_my_placement_readiness(
    student_profile: StudentProfile, db: AsyncSession
) -> Dict[str, Any]:
    """
    Returns ML XGBoost placement readiness inference for this student.
    Never invents scores; falls back gracefully if data is insufficient.
    """
    features_info = await extract_student_features(db, student_profile.id)
    model = get_readiness_model()
    prediction = model.predict(features_info)
    student_name = await _get_student_name(student_profile, db)

    return {
        "student_name": student_name,
        "status": prediction.get("status", "READY"),
        "readiness_score": prediction.get("readiness_score", 0.0),
        "readiness_category": prediction.get("readiness_category", "NEEDS_IMPROVEMENT"),
        "confidence": prediction.get("confidence", 0.0),
        "probabilities": prediction.get("probabilities", {}),
        "strengths": prediction.get("contributing_factors", {}).get("strengths", []),
        "improvement_areas": prediction.get("contributing_factors", {}).get("areas_for_improvement", []),
        "feature_highlights": {
            "aptitude_accuracy": features_info.get("features", {}).get("aptitude_accuracy", 0.0),
            "coding_score": features_info.get("features", {}).get("coding_score", 0.0),
            "topic_mastery": features_info.get("features", {}).get("topic_mastery", 0.0),
            "assessment_score": features_info.get("features", {}).get("assessment_score", 0.0),
            "improvement_trend": features_info.get("features", {}).get("improvement_trend", 0.0),
        },
        "has_sufficient_data": features_info.get("has_sufficient_data", False),
    }


async def get_my_weak_topics(
    student_profile: StudentProfile, db: AsyncSession, limit: int = 5
) -> Dict[str, Any]:
    """
    Returns authenticated student's weakest topics based on actual practice and test results.
    """
    analytics = await AdaptiveEngine.get_student_topic_analytics(db, student_profile.id)
    practiced = [a for a in analytics if a["questions_attempted"] >= 1]

    # Weak if accuracy < 60%
    weak = [a for a in practiced if (a["accuracy"] is not None and a["accuracy"] < 60.0)]
    weak.sort(key=lambda x: (x["accuracy"] if x["accuracy"] is not None else 0, -x["questions_attempted"]))

    result_topics = []
    for w in weak[:limit]:
        result_topics.append({
            "topic_id": w["topic_id"],
            "topic": w["topic_name"],
            "accuracy": w["accuracy"],
            "questions_attempted": w["questions_attempted"],
            "questions_correct": w["questions_correct"],
            "skill_rating": w["skill_rating"],
            "recommended_action": "Foundational practice recommended to rebuild competency",
        })

    return {
        "weak_topics_count": len(result_topics),
        "topics": result_topics,
        "has_data": len(practiced) > 0,
    }


async def get_my_strong_topics(
    student_profile: StudentProfile, db: AsyncSession, limit: int = 5
) -> Dict[str, Any]:
    """
    Returns authenticated student's strongest mastered topics.
    """
    analytics = await AdaptiveEngine.get_student_topic_analytics(db, student_profile.id)
    practiced = [a for a in analytics if a["questions_attempted"] >= 2]

    # Strong if accuracy >= 70%
    strong = [a for a in practiced if (a["accuracy"] is not None and a["accuracy"] >= 70.0)]
    strong.sort(key=lambda x: (-(x["accuracy"] if x["accuracy"] is not None else 0), -x["questions_attempted"]))

    result_topics = []
    for s in strong[:limit]:
        result_topics.append({
            "topic_id": s["topic_id"],
            "topic": s["topic_name"],
            "accuracy": s["accuracy"],
            "questions_attempted": s["questions_attempted"],
            "questions_correct": s["questions_correct"],
            "skill_rating": s["skill_rating"],
        })

    return {
        "strong_topics_count": len(result_topics),
        "topics": result_topics,
        "has_data": len(practiced) > 0,
    }


async def get_my_recent_attempts(
    student_profile: StudentProfile, db: AsyncSession, limit: int = 5
) -> Dict[str, Any]:
    """
    Returns only the necessary summary of recent graded test attempts.
    """
    stmt = (
        select(TestAttempt)
        .where(
            TestAttempt.student_id == student_profile.id,
            TestAttempt.status == AttemptStatus.GRADED,
        )
        .options(selectinload(TestAttempt.test))
        .order_by(TestAttempt.submitted_at.desc().nullslast(), TestAttempt.id.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    attempts = res.scalars().all()

    items = []
    for a in attempts:
        items.append({
            "attempt_id": a.id,
            "assessment": a.test.title if a.test else "Assessment",
            "type": a.test.test_type.value if a.test and a.test.test_type else "APTITUDE",
            "score": round(a.score or 0.0, 1),
            "max_score": round(a.max_score or 100.0, 1),
            "percentage": round(a.percentage or 0.0, 1),
            "passed": (a.percentage or 0.0) >= (a.test.passing_marks if a.test and a.test.passing_marks else 40.0),
            "date": a.submitted_at.strftime("%Y-%m-%d") if a.submitted_at else "Recent",
        })

    return {
        "recent_attempts": items,
        "total_returned": len(items),
    }


async def get_my_aptitude_performance(
    student_profile: StudentProfile, db: AsyncSession
) -> Dict[str, Any]:
    """
    Returns detailed aptitude breakdown by category (Quantitative, Logical, Verbal).
    """
    # Join TopicProgress -> Topic -> Subject
    stmt = (
        select(TopicProgress, Topic, Subject)
        .join(Topic, TopicProgress.topic_id == Topic.id)
        .join(Subject, Topic.subject_id == Subject.id)
        .where(
            TopicProgress.student_id == student_profile.id,
            Subject.category == SubjectCategory.APTITUDE,
        )
    )
    res = await db.execute(stmt)
    rows = res.all()

    category_stats: Dict[str, Dict[str, Any]] = {}
    total_attempted = 0
    total_correct = 0

    for prog, topic, subj in rows:
        c_name = subj.name
        if c_name not in category_stats:
            category_stats[c_name] = {"attempted": 0, "correct": 0, "topics_practiced": 0}
        category_stats[c_name]["attempted"] += prog.questions_attempted
        category_stats[c_name]["correct"] += prog.questions_correct
        if prog.questions_attempted > 0:
            category_stats[c_name]["topics_practiced"] += 1
        total_attempted += prog.questions_attempted
        total_correct += prog.questions_correct

    breakdown = []
    for cat, stat in category_stats.items():
        att = stat["attempted"]
        cor = stat["correct"]
        acc = round((cor / att * 100.0), 1) if att > 0 else None
        breakdown.append({
            "subject": cat,
            "accuracy": acc,
            "questions_attempted": att,
            "topics_practiced": stat["topics_practiced"],
        })

    overall_acc = round(total_correct / total_attempted * 100.0, 1) if total_attempted > 0 else None

    return {
        "overall_aptitude_accuracy": overall_acc,
        "total_questions_attempted": total_attempted,
        "subject_breakdown": breakdown,
        "has_data": total_attempted > 0,
    }


async def get_my_coding_performance(
    student_profile: StudentProfile, db: AsyncSession
) -> Dict[str, Any]:
    """
    Returns authenticated student's coding metrics:
    Problems attempted, solved, pass rate, difficulty breakdown, languages used.
    """
    # Query code submissions
    stmt = (
        select(CodeSubmission)
        .where(CodeSubmission.student_id == student_profile.id)
        .options(selectinload(CodeSubmission.coding_question))
    )
    res = await db.execute(stmt)
    submissions = res.scalars().all()

    if not submissions:
        return {
            "problems_attempted": 0,
            "problems_solved": 0,
            "success_rate": 0.0,
            "languages_used": [],
            "difficulty_breakdown": {"EASY": 0, "MEDIUM": 0, "HARD": 0},
            "recent_verdicts": [],
            "has_data": False,
        }

    attempted_problems = set()
    solved_problems = set()
    languages: Dict[str, int] = {}
    diff_solved: Dict[str, int] = {"EASY": 0, "MEDIUM": 0, "HARD": 0}

    for sub in submissions:
        q_id = sub.coding_question_id
        attempted_problems.add(q_id)
        if sub.language:
            languages[sub.language] = languages.get(sub.language, 0) + 1
        if sub.verdict == SubmissionVerdict.ACCEPTED:
            solved_problems.add(q_id)
            if sub.coding_question and sub.coding_question.difficulty:
                d = sub.coding_question.difficulty.upper()
                if d in diff_solved:
                    diff_solved[d] += 1

    success_rate = round(len(solved_problems) / len(attempted_problems) * 100.0, 1) if attempted_problems else 0.0

    return {
        "problems_attempted": len(attempted_problems),
        "problems_solved": len(solved_problems),
        "total_submissions": len(submissions),
        "success_rate": success_rate,
        "languages_used": list(languages.keys()),
        "difficulty_solved": diff_solved,
        "has_data": True,
    }


async def get_my_learning_progress(
    student_profile: StudentProfile, db: AsyncSession
) -> Dict[str, Any]:
    """
    Returns learning module progress: lessons completed, topics covered.
    """
    # Completed lessons
    stmt = (
        select(func.count(LessonCompletion.id))
        .where(LessonCompletion.student_id == student_profile.id)
    )
    comp_res = await db.execute(stmt)
    lessons_completed = comp_res.scalar() or 0

    # Total lessons available
    total_lessons_res = await db.execute(select(func.count(Lesson.id)))
    total_lessons = total_lessons_res.scalar() or 0

    # Topics attempted in practice
    tp_stmt = (
        select(func.count(TopicProgress.id))
        .where(
            TopicProgress.student_id == student_profile.id,
            TopicProgress.questions_attempted > 0,
        )
    )
    topics_practiced_res = await db.execute(tp_stmt)
    topics_practiced = topics_practiced_res.scalar() or 0

    total_topics_res = await db.execute(select(func.count(Topic.id)))
    total_topics = total_topics_res.scalar() or 0

    return {
        "lessons_completed": lessons_completed,
        "total_lessons": total_lessons,
        "lesson_completion_pct": round(lessons_completed / total_lessons * 100.0, 1) if total_lessons > 0 else 0.0,
        "topics_practiced": topics_practiced,
        "total_topics": total_topics,
        "topic_coverage_pct": round(topics_practiced / total_topics * 100.0, 1) if total_topics > 0 else 0.0,
    }


async def get_my_recommended_topics(
    student_profile: StudentProfile, db: AsyncSession
) -> Dict[str, Any]:
    """
    Uses existing AdaptiveEngine to produce personalized study recommendation.
    """
    insights = await AdaptiveEngine.get_personalization_insights(db, student_profile.id)
    return {
        "recommendation_banner": insights.get("recommendation_banner", ""),
        "recommended_topic_id": insights.get("recommended_topic_id"),
        "top_weak_topics": [
            {"topic": w["topic_name"], "accuracy": w["accuracy"]}
            for w in insights.get("weak_topics", [])
        ],
        "top_strong_topics": [
            {"topic": s["topic_name"], "accuracy": s["accuracy"]}
            for s in insights.get("strong_topics", [])
        ],
        "tips": [
            {"title": t["title"], "description": t["description"]}
            for t in insights.get("tips", [])
        ],
    }


async def get_my_question_history(
    student_profile: StudentProfile, db: AsyncSession, limit: int = 10
) -> Dict[str, Any]:
    """
    Returns summary of student's question exposure history.
    """
    stmt = (
        select(StudentQuestionHistory)
        .where(StudentQuestionHistory.student_id == student_profile.id)
        .order_by(StudentQuestionHistory.last_seen_at.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    history = res.scalars().all()

    total_seen = len(history)
    reinforce_candidates = [
        h.question_id for h in history if h.times_incorrect > h.times_correct
    ]

    return {
        "total_tracked_questions": total_seen,
        "needs_reinforcement_count": len(reinforce_candidates),
        "sample_history": [
            {
                "question_id": h.question_id,
                "times_seen": h.times_seen,
                "times_correct": h.times_correct,
                "times_incorrect": h.times_incorrect,
            }
            for h in history[:5]
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. Contextual Question Explanation with Assessment Protection
# ─────────────────────────────────────────────────────────────────────────────

async def get_current_question_context(
    student_profile: StudentProfile,
    db: AsyncSession,
    question_id: Optional[int] = None,
    test_attempt_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Retrieves question context for pedagogical explanation.
    STRICT SECURITY RULE:
    If this question belongs to an ACTIVE PROCTORED ASSESSMENT in progress,
    refuse to provide correct answers/hints to preserve assessment integrity.
    """
    if not question_id:
        return {"error": "NO_QUESTION_SPECIFIED", "message": "Please specify which question you would like explained."}

    # 1. Check if question is in ANY active test attempt for this student
    active_test = await get_active_assessment(student_profile, db)
    if active_test:
        # Check if question_id is in the active test attempt
        att_res = await db.execute(
            select(TestAttempt).where(TestAttempt.id == active_test["attempt_id"])
        )
        curr_attempt = att_res.scalar_one_or_none()
        if curr_attempt and curr_attempt.question_order:
            if question_id in curr_attempt.question_order:
                return {
                    "restricted": True,
                    "reason": "ACTIVE_ASSESSMENT",
                    "message": (
                        "You currently have an active proctored assessment in progress. "
                        "In accordance with CareerForge exam integrity policies, I cannot provide "
                        "hints, answers, or explanations for active assessment questions until "
                        "your assessment has been submitted."
                    ),
                }

    # 2. Load Question with options
    q_res = await db.execute(
        select(Question)
        .where(Question.id == question_id)
        .options(selectinload(Question.options), selectinload(Question.topic))
    )
    question = q_res.scalar_one_or_none()
    if not question:
        return {"error": "QUESTION_NOT_FOUND", "message": "Question not found in the question bank."}

    # 3. Check student's recent practice or test answer for this question
    selected_option_id = None
    selected_option_text = None
    is_correct = None

    if test_attempt_id:
        ans_res = await db.execute(
            select(TestAnswer)
            .where(
                TestAnswer.attempt_id == test_attempt_id,
                TestAnswer.question_id == question_id,
            )
        )
        answer = ans_res.scalar_one_or_none()
        if answer:
            selected_option_id = answer.selected_option_id
            is_correct = answer.is_correct
    else:
        # Check practice attempt
        p_res = await db.execute(
            select(PracticeAttempt)
            .where(
                PracticeAttempt.student_id == student_profile.id,
                PracticeAttempt.question_id == question_id,
            )
            .order_by(PracticeAttempt.attempted_at.desc())
            .limit(1)
        )
        p_att = p_res.scalar_one_or_none()
        if p_att:
            selected_option_id = p_att.selected_option_id
            is_correct = p_att.is_correct

    correct_option = next((o for o in question.options if o.is_correct), None)
    options_summary = []
    for opt in question.options:
        is_sel = (opt.id == selected_option_id)
        if is_sel:
            selected_option_text = opt.text
        options_summary.append({
            "id": opt.id,
            "text": opt.text,
            "is_selected": is_sel,
            "is_correct": opt.is_correct,
        })

    return {
        "restricted": False,
        "question_id": question.id,
        "question_text": question.text,
        "topic": question.topic.name if question.topic else "General",
        "difficulty": question.difficulty.value if hasattr(question.difficulty, "value") else str(question.difficulty),
        "options": options_summary,
        "student_selected_text": selected_option_text or "Not recorded",
        "is_student_correct": is_correct,
        "correct_option_text": correct_option.text if correct_option else "N/A",
        "official_explanation": question.explanation or "No explanation stored in bank.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. Adaptive Practice Question Selection
# ─────────────────────────────────────────────────────────────────────────────

async def get_my_adaptive_practice(
    student_profile: StudentProfile,
    db: AsyncSession,
    topic_name: Optional[str] = None,
    topic_id: Optional[int] = None,
    count: int = 5,
) -> Dict[str, Any]:
    """
    Surfaces real practice questions from the question bank using the existing
    AdaptiveEngine (Rasch IRT + Elo + no-repeat logic).
    """
    target_topic_id = topic_id
    target_topic_name = topic_name

    # Resolve topic by name if provided
    if not target_topic_id and topic_name:
        t_res = await db.execute(
            select(Topic).where(Topic.name.ilike(f"%{topic_name.strip()}%")).limit(1)
        )
        t = t_res.scalar_one_or_none()
        if t:
            target_topic_id = t.id
            target_topic_name = t.name

    # If no topic specified, target student's weakest topic
    if not target_topic_id:
        weak_data = await get_my_weak_topics(student_profile, db, limit=1)
        if weak_data.get("topics"):
            target_topic_id = weak_data["topics"][0]["topic_id"]
            target_topic_name = weak_data["topics"][0]["topic"]

    # Generate session using existing AdaptiveEngine
    count = max(1, min(10, count))
    questions, insights = await AdaptiveEngine.generate_adaptive_session(
        db=db,
        student_id=student_profile.id,
        topic_id=target_topic_id,
        count=count,
    )

    questions_out = []
    for q in questions:
        topic_name_val = target_topic_name
        if "topic" in q.__dict__ and q.topic:
            topic_name_val = q.topic.name
        questions_out.append({
            "id": q.id,
            "text": q.text,
            "difficulty": q.difficulty.value if hasattr(q.difficulty, "value") else str(q.difficulty),
            "points": q.points,
            "topic": topic_name_val or "Practice",
            "options": [{"id": o.id, "text": o.text} for o in q.options],
        })

    return {
        "topic_id": target_topic_id,
        "topic_name": target_topic_name or "Personalized Adaptive Practice",
        "questions_count": len(questions_out),
        "questions": questions_out,
        "recommendation_tip": insights.get("recommendation_banner", ""),
    }
