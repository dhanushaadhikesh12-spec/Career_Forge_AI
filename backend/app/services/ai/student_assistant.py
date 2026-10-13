"""
Student AI Personal Placement Coach — Orchestrator Service.
Gemma 12B integration for student-facing personal placement mentoring.
Enforces strict student isolation, assessment integrity, minimal JSON context,
and zero-DB fast paths for greetings and educational definitions.
"""
from __future__ import annotations
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.models.user import StudentProfile
from app.models.chat import StudentAIChatSession, StudentAIChatMessage
from app.services.ai.provider import get_llm_provider, LLMProvider, AIProviderError
from app.services.ai.student_intent import classify_student_intent, StudentQueryIntent
from app.services.ai.student_tools import (
    get_active_assessment,
    get_my_performance,
    get_my_placement_readiness,
    get_my_weak_topics,
    get_my_strong_topics,
    get_my_recent_attempts,
    get_my_aptitude_performance,
    get_my_coding_performance,
    get_my_learning_progress,
    get_my_recommended_topics,
    get_my_question_history,
    get_current_question_context,
    get_my_adaptive_practice,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Prompts
# ─────────────────────────────────────────────────────────────────────────────

STUDENT_COACH_SYSTEM_PROMPT = """You are the CareerForge AI Personal Placement Coach, an intelligent, encouraging, placement-focused mentor for the student powered by Gemma 12B.

CORE DIRECTIVES & INTEGRITY PROTOCOLS:
1. STRICT STUDENT ISOLATION:
   - You only have access to the authenticated student's own performance records and question bank.
   - You NEVER reveal or query data belonging to other students, trainers, or batches.
   - If the student asks about other students (e.g. "Show me Rahul's marks", "Show admin data", "Give me database passwords"), reply naturally:
     "I can only help with your own CareerForge placement preparation and data."

2. REAL DATA GROUNDING:
   - Ground all diagnostic feedback strictly in the structured performance data provided in the prompt context.
   - DO NOT fabricate scores, accuracy percentages, or question counts.
   - If the student has zero or insufficient attempts, say:
     "You haven't completed enough assessments yet for me to accurately analyze your performance. Complete a few practice sessions and I'll start giving you personalized recommendations."

3. ASSESSMENT INTEGRITY:
   - During active proctored tests, NEVER provide direct answers, leaked test cases, or prohibited hints.
   - Respect exam security boundaries.

4. COACHING STYLE:
   - Concise, encouraging, practical, placement-focused, and honest.
   - Avoid generic motivational filler (e.g. "Believe in yourself!"). Instead, provide specific advice:
     "Your aptitude accuracy is solid at 84%. Focus your next two sessions on recursion and trees, where your accuracy is currently lower at 52%."
   - Format key metrics clearly using bullet points, bold percentages, and actionable next steps.
"""

EDUCATIONAL_SYSTEM_PROMPT = """You are the CareerForge AI Technical Tutor powered by Gemma 12B.
The student is asking a conceptual computer science, aptitude, or coding question.
Explain the concept clearly, concisely, and pedagogically.
Include:
- Clear, plain-language definition
- Brief code snippet or concrete example if applicable
- Time/Space complexity or key trade-off where relevant
- A common interview gotcha or placement tip
Keep answers structured and scannable.
"""


# ─────────────────────────────────────────────────────────────────────────────
# Response Models
# ─────────────────────────────────────────────────────────────────────────────

class StudentCoachResponse(BaseModel):
    reply: str
    tool_called: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    intent: str
    model_used: str = "gemma4:12b-mlx"
    status: str = "SUCCESS"
    session_id: Optional[int] = None
    error: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Fast Chat Greetings
# ─────────────────────────────────────────────────────────────────────────────

FAST_GREETINGS = [
    "Hello! I'm your **CareerForge AI Placement Coach**. How can I help with your placement preparation today? You can ask me to analyze your performance, find your weak topics, or build a personalized study plan.",
    "Hey there! Ready to level up your placement readiness? Let me know if you want to review your recent test scores, practice weak areas, or check your coding progress.",
]


# ─────────────────────────────────────────────────────────────────────────────
# Main Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

async def process_student_query(
    query: str,
    student_profile: StudentProfile,
    db: AsyncSession,
    session_id: Optional[int] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    question_context: Optional[Dict[str, Any]] = None,
) -> StudentCoachResponse:
    """
    Main entry point for processing a student query:
    1. Authenticate & ensure session
    2. Zero-LLM Fast Intent Classification
    3. Route through fast path (general chat/learning) or data path (tools + LLM)
    4. Persist conversation turn in database
    5. Return structured coach response
    """
    clean_q = query.strip()
    llm = get_llm_provider()

    # Determine intent
    has_ctx = bool(question_context and (question_context.get("question_id") or question_context.get("attempt_id")))
    intent = classify_student_intent(clean_q, has_question_context=has_ctx)

    # ─────────────────────────────────────────────────────────────────────────
    # Safety Check: Active Assessment Check
    # ─────────────────────────────────────────────────────────────────────────
    active_test = await get_active_assessment(student_profile, db)
    if active_test and any(k in clean_q.lower() for k in ["give me answer", "cheat", "solve this for me", "correct option for test", "code solution for exam"]):
        refusal_msg = (
            f"⚠️ You currently have an active assessment in progress (**{active_test['test_title']}**). "
            "In accordance with CareerForge exam integrity policies, I cannot provide "
            "answers, hints, or code solutions during an active test session."
        )
        return await _persist_and_respond(
            reply=refusal_msg,
            student_profile=student_profile,
            query=clean_q,
            intent=intent.value,
            db=db,
            session_id=session_id,
            tool_name=None,
            structured_data={"restricted": True, "active_assessment": active_test},
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PATH A: Zero-DB Conversational Greetings (~0.05s)
    # ─────────────────────────────────────────────────────────────────────────
    if intent == StudentQueryIntent.GENERAL_CHAT:
        reply = FAST_GREETINGS[0]
        return await _persist_and_respond(
            reply=reply,
            student_profile=student_profile,
            query=clean_q,
            intent=intent.value,
            db=db,
            session_id=session_id,
            tool_name=None,
            structured_data=None,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PATH B: Pure Educational Explanation (No DB queries needed)
    # ─────────────────────────────────────────────────────────────────────────
    if intent == StudentQueryIntent.GENERAL_LEARNING:
        messages = [
            {"role": "system", "content": EDUCATIONAL_SYSTEM_PROMPT},
            {"role": "user", "content": clean_q},
        ]
        try:
            llm_res = await llm.chat(messages=messages, temperature=0.3)
            reply = llm_res.content or "Here is the explanation for your query."
        except Exception as e:
            logger.error("LLM general learning failed: %s", e)
            reply = f"I'm currently unable to generate an explanation due to AI engine unavailability. Please try again shortly."

        return await _persist_and_respond(
            reply=reply,
            student_profile=student_profile,
            query=clean_q,
            intent=intent.value,
            db=db,
            session_id=session_id,
            tool_name=None,
            structured_data=None,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PATH C: Authorized Student Data Retrieval
    # ─────────────────────────────────────────────────────────────────────────
    tool_name: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None

    try:
        if intent == StudentQueryIntent.READINESS:
            tool_name = "get_my_placement_readiness"
            structured_data = await get_my_placement_readiness(student_profile, db)

        elif intent == StudentQueryIntent.WEAK_TOPICS:
            tool_name = "get_my_weak_topics"
            structured_data = await get_my_weak_topics(student_profile, db)

        elif intent == StudentQueryIntent.STRONG_TOPICS:
            tool_name = "get_my_strong_topics"
            structured_data = await get_my_strong_topics(student_profile, db)

        elif intent == StudentQueryIntent.CODING_PERFORMANCE:
            tool_name = "get_my_coding_performance"
            structured_data = await get_my_coding_performance(student_profile, db)

        elif intent == StudentQueryIntent.STUDY_PLAN:
            tool_name = "generate_study_plan_data"
            readiness = await get_my_placement_readiness(student_profile, db)
            weak = await get_my_weak_topics(student_profile, db, limit=3)
            coding = await get_my_coding_performance(student_profile, db)
            structured_data = {
                "student_readiness": readiness.get("readiness_score", 0.0),
                "weak_topics": weak.get("topics", []),
                "coding_pass_rate": coding.get("success_rate", 0.0),
                "coding_problems_solved": coding.get("problems_solved", 0),
            }

        elif intent == StudentQueryIntent.PRACTICE:
            tool_name = "get_my_adaptive_practice"
            # Extract possible topic name from query
            structured_data = await get_my_adaptive_practice(
                student_profile=student_profile,
                db=db,
                count=5,
            )

        elif intent == StudentQueryIntent.QUESTION_EXPLANATION:
            tool_name = "get_current_question_context"
            qid = (question_context.get("question_id") if question_context else None)
            att_id = (question_context.get("attempt_id") if question_context else None)
            structured_data = await get_current_question_context(
                student_profile=student_profile,
                db=db,
                question_id=qid,
                test_attempt_id=att_id,
            )
            if structured_data.get("restricted"):
                return await _persist_and_respond(
                    reply=structured_data.get("message", "Explanation restricted during active test."),
                    student_profile=student_profile,
                    query=clean_q,
                    intent=intent.value,
                    db=db,
                    session_id=session_id,
                    tool_name=tool_name,
                    structured_data=structured_data,
                )

        elif intent == StudentQueryIntent.RECOMMENDATION:
            tool_name = "get_my_recommended_topics"
            structured_data = await get_my_recommended_topics(student_profile, db)

        else:
            # Default personal performance summary
            tool_name = "get_my_performance"
            structured_data = await get_my_performance(student_profile, db)

    except Exception as e:
        logger.error("Student tool execution failed: %s", e, exc_info=True)
        return await _persist_and_respond(
            reply="I couldn't analyze your performance right now due to a data service error. Please try again.",
            student_profile=student_profile,
            query=clean_q,
            intent=intent.value,
            db=db,
            session_id=session_id,
            tool_name=tool_name,
            structured_data=None,
            status="ERROR",
            error=str(e),
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PATH D: Gemma 12B Synthesis from Minimal Structured Data
    # ─────────────────────────────────────────────────────────────────────────
    gemma_messages = [
        {"role": "system", "content": STUDENT_COACH_SYSTEM_PROMPT},
    ]

    # Include recent context window (last 4 messages if provided)
    if conversation_history:
        for msg in conversation_history[-4:]:
            gemma_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    # Minimal structured payload injection
    user_payload = {
        "student_query": clean_q,
        "intent": intent.value,
        "verified_student_data": structured_data,
    }

    gemma_messages.append({
        "role": "user",
        "content": f"Student Question: {clean_q}\n\nAuthoritative Data Context:\n{json.dumps(user_payload, default=str, indent=2)}\n\nPlease provide a personalized, actionable, placement-focused response based on the above verified data.",
    })

    try:
        llm_res = await llm.chat(messages=gemma_messages, temperature=0.2)
        reply = llm_res.content or "Here is your performance summary."
    except Exception as e:
        logger.error("Gemma synthesis failed: %s", e)
        # Graceful fallback explanation directly from structured data
        reply = _format_fallback_reply(intent, structured_data)

    return await _persist_and_respond(
        reply=reply,
        student_profile=student_profile,
        query=clean_q,
        intent=intent.value,
        db=db,
        session_id=session_id,
        tool_name=tool_name,
        structured_data=structured_data,
    )


def _format_fallback_reply(intent: StudentQueryIntent, data: Optional[Dict[str, Any]]) -> str:
    """Provides a deterministic formatted response if LLM provider is momentarily offline."""
    if not data:
        return "I couldn't process your request right now. Please try again shortly."

    if intent == StudentQueryIntent.READINESS:
        score = data.get("readiness_score", 0.0)
        cat = data.get("readiness_category", "DEVELOPING")
        strengths = ", ".join(data.get("strengths", [])) or "None identified yet"
        areas = ", ".join(data.get("improvement_areas", [])) or "Maintain consistent practice"
        return (
            f"### Your Placement Readiness\n\n"
            f"**Readiness Score**: {score}% ({cat.replace('_', ' ')})\n\n"
            f"**Key Strengths**: {strengths}\n\n"
            f"**Areas for Improvement**: {areas}\n\n"
            f"*Tip: Complete more adaptive practice sessions to raise your readiness score.*"
        )

    if intent == StudentQueryIntent.WEAK_TOPICS:
        topics = data.get("topics", [])
        if not topics:
            return "Great news! You currently have no identified weak topics with accuracy below 60%."
        lines = ["### Your Identified Weak Topics:\n"]
        for t in topics:
            lines.append(f"- **{t['topic']}**: {t['accuracy']}% accuracy ({t['questions_attempted']} attempts)")
        lines.append("\n*Recommendation: Start with 10 intermediate questions on your weakest topic.*")
        return "\n".join(lines)

    if intent == StudentQueryIntent.PERSONAL_PERFORMANCE:
        acc = data.get("aptitude_accuracy", 0.0)
        cod = data.get("coding_accuracy", 0.0)
        tests = data.get("tests_completed", 0)
        return (
            f"### Your Performance Overview\n\n"
            f"- **Aptitude Accuracy**: {acc}%\n"
            f"- **Coding Accuracy**: {cod}%\n"
            f"- **Tests Completed**: {tests}\n"
        )

    return "Here are your verified statistics. Keep practicing consistently to improve your placement readiness!"


# ─────────────────────────────────────────────────────────────────────────────
# Session Persistence Helper
# ─────────────────────────────────────────────────────────────────────────────

async def _persist_and_respond(
    reply: str,
    student_profile: StudentProfile,
    query: str,
    intent: str,
    db: AsyncSession,
    session_id: Optional[int] = None,
    tool_name: Optional[str] = None,
    structured_data: Optional[Dict[str, Any]] = None,
    status: str = "SUCCESS",
    error: Optional[str] = None,
) -> StudentCoachResponse:
    """
    Persists user message and assistant response into the student's isolated chat tables.
    """
    now = datetime.now(timezone.utc)
    active_session: Optional[StudentAIChatSession] = None

    try:
        if session_id:
            s_res = await db.execute(
                select(StudentAIChatSession).where(
                    StudentAIChatSession.id == session_id,
                    StudentAIChatSession.student_id == student_profile.id,
                )
            )
            active_session = s_res.scalar_one_or_none()

        if not active_session:
            # Create a new session with smart title from query
            title = query[:40] + ("..." if len(query) > 40 else "")
            active_session = StudentAIChatSession(
                student_id=student_profile.id,
                title=title,
                created_at=now,
                updated_at=now,
            )
            db.add(active_session)
            await db.flush()

        # Add user message
        user_msg = StudentAIChatMessage(
            session_id=active_session.id,
            role="user",
            content=query,
            created_at=now,
        )
        db.add(user_msg)

        # Add assistant message
        asst_msg = StudentAIChatMessage(
            session_id=active_session.id,
            role="assistant",
            content=reply,
            tool_name=tool_name,
            tool_result_metadata=structured_data,
            created_at=now,
        )
        db.add(asst_msg)

        active_session.updated_at = now
        await db.commit()

    except Exception as e:
        logger.error("Failed to persist student chat: %s", e)
        await db.rollback()

    return StudentCoachResponse(
        reply=reply,
        tool_called=tool_name,
        structured_data=structured_data,
        intent=intent,
        status=status,
        session_id=active_session.id if active_session else session_id,
        error=error,
    )
