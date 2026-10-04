"""
Trainer AI Assistant persistent chat models.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class AIChatSession(Base):
    __tablename__ = "ai_chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), default="New Conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    # Relationships
    messages: Mapped[List["AIChatMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="AIChatMessage.created_at",
    )


class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("ai_chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tool_result_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    session: Mapped["AIChatSession"] = relationship(back_populates="messages")
