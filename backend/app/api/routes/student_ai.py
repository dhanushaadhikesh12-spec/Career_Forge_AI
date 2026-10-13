"""
Student AI Personal Placement Coach Routes.
Provides isolated, student-scoped chat session management and Gemma 12B coaching.
Security: Derives identity strictly from JWT token via get_student_profile.
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field, ConfigDict

from app.db.database import get_db
from app.api.deps import get_student_profile
from app.models.user import StudentProfile
from app.models.chat import StudentAIChatSession, StudentAIChatMessage
from app.services.ai.student_assistant import (
    process_student_query,
    StudentCoachResponse,
)
from app.services.ai.provider import get_llm_provider
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students/coach", tags=["Student AI Placement Coach"])


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────────────────────────────────────

class StudentAIChatSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class StudentAIChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    role: str
    content: str
    tool_name: Optional[str] = None
    tool_result_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class StudentAIChatSessionDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[StudentAIChatMessageOut] = []


class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Coaching Session"


class UpdateSessionRequest(BaseModel):
    title: str


class StudentCoachChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[int] = None
    conversation_history: Optional[List[Dict[str, str]]] = None
    question_context: Optional[Dict[str, Any]] = None


# ─────────────────────────────────────────────────────────────────────────────
# Status & Diagnostics
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/status")
async def get_coach_status(
    profile: StudentProfile = Depends(get_student_profile),
):
    """Returns AI Provider status and model availability."""
    provider = get_llm_provider()
    try:
        available = await provider.is_available()
    except Exception:
        available = False

    return {
        "available": available,
        "provider": settings.AI_PROVIDER,
        "model": settings.OLLAMA_MODEL,
        "mode": "STUDENT_COACH",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Chat Sessions CRUD (Strictly Isolated to Authenticated Student)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/sessions", response_model=List[StudentAIChatSessionOut])
async def list_student_chat_sessions(
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """Lists all coaching sessions belonging to the authenticated student."""
    stmt = (
        select(StudentAIChatSession)
        .where(StudentAIChatSession.student_id == profile.id)
        .options(selectinload(StudentAIChatSession.messages))
        .order_by(StudentAIChatSession.updated_at.desc())
    )
    res = await db.execute(stmt)
    sessions = res.scalars().all()

    return [
        StudentAIChatSessionOut(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=len(s.messages) if s.messages else 0,
        )
        for s in sessions
    ]


@router.post("/sessions", response_model=StudentAIChatSessionOut)
async def create_student_chat_session(
    body: CreateSessionRequest,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new coaching session for the authenticated student."""
    now = datetime.now(timezone.utc)
    sess = StudentAIChatSession(
        student_id=profile.id,
        title=body.title or "New Coaching Session",
        created_at=now,
        updated_at=now,
    )
    db.add(sess)
    await db.commit()
    await db.refresh(sess)

    return StudentAIChatSessionOut(
        id=sess.id,
        title=sess.title,
        created_at=sess.created_at,
        updated_at=sess.updated_at,
        message_count=0,
    )


@router.get("/sessions/{session_id}", response_model=StudentAIChatSessionDetailOut)
async def get_student_chat_session(
    session_id: int,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full conversation history for a student's session."""
    stmt = (
        select(StudentAIChatSession)
        .where(
            StudentAIChatSession.id == session_id,
            StudentAIChatSession.student_id == profile.id,
        )
        .options(selectinload(StudentAIChatSession.messages))
    )
    res = await db.execute(stmt)
    sess = res.scalar_one_or_none()
    if not sess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching session not found or access denied.",
        )

    return StudentAIChatSessionDetailOut(
        id=sess.id,
        title=sess.title,
        created_at=sess.created_at,
        updated_at=sess.updated_at,
        messages=[
            StudentAIChatMessageOut(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                tool_name=m.tool_name,
                tool_result_metadata=m.tool_result_metadata,
                created_at=m.created_at,
            )
            for m in sess.messages
        ],
    )


@router.patch("/sessions/{session_id}", response_model=StudentAIChatSessionOut)
async def update_student_chat_session(
    session_id: int,
    body: UpdateSessionRequest,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """Updates the title of a student's coaching session."""
    stmt = select(StudentAIChatSession).where(
        StudentAIChatSession.id == session_id,
        StudentAIChatSession.student_id == profile.id,
    )
    res = await db.execute(stmt)
    sess = res.scalar_one_or_none()
    if not sess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching session not found or access denied.",
        )

    sess.title = body.title
    sess.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(sess)

    return StudentAIChatSessionOut(
        id=sess.id,
        title=sess.title,
        created_at=sess.created_at,
        updated_at=sess.updated_at,
        message_count=0,
    )


@router.delete("/sessions/{session_id}")
async def delete_student_chat_session(
    session_id: int,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a student's coaching session and its message history."""
    stmt = select(StudentAIChatSession).where(
        StudentAIChatSession.id == session_id,
        StudentAIChatSession.student_id == profile.id,
    )
    res = await db.execute(stmt)
    sess = res.scalar_one_or_none()
    if not sess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching session not found or access denied.",
        )

    await db.delete(sess)
    await db.commit()
    return {"message": "Session deleted successfully."}


# ─────────────────────────────────────────────────────────────────────────────
# Chat Interaction Endpoint
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=StudentCoachResponse)
async def student_coach_chat(
    req: StudentCoachChatRequest,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Student AI Personal Placement Coach interaction endpoint.
    Strictly derives student identity from authenticated JWT.
    Enforces intent routing, authorized tool execution, and session persistence.
    """
    return await process_student_query(
        query=req.query,
        student_profile=profile,
        db=db,
        session_id=req.session_id,
        conversation_history=req.conversation_history,
        question_context=req.question_context,
    )
