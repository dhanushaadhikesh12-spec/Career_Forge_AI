"""
Tests, test attempts, answers, and proctoring event models.
"""
from __future__ import annotations
import enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, Enum as SAEnum, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class TestType(str, enum.Enum):
    APTITUDE = "APTITUDE"
    CODING = "CODING"
    MIXED = "MIXED"


class TestStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class AttemptStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    TIMED_OUT = "TIMED_OUT"
    GRADED = "GRADED"


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    test_type: Mapped[TestType] = mapped_column(SAEnum(TestType), default=TestType.APTITUDE)
    status: Mapped[TestStatus] = mapped_column(SAEnum(TestStatus), default=TestStatus.DRAFT)
    batch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("batches.id", ondelete="SET NULL"), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    total_marks: Mapped[int] = mapped_column(Integer, default=100)
    passing_marks: Mapped[int] = mapped_column(Integer, default=40)
    instructions: Mapped[Optional[str]] = mapped_column(Text)
    randomize_questions: Mapped[bool] = mapped_column(Boolean, default=True)
    show_results_immediately: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    # Relationships
    test_questions: Mapped[List["TestQuestion"]] = relationship(back_populates="test", cascade="all, delete-orphan")
    attempts: Mapped[List["TestAttempt"]] = relationship(back_populates="test", cascade="all, delete-orphan")


class TestQuestion(Base):
    __tablename__ = "test_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[Optional[int]] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=True)
    coding_question_id: Mapped[Optional[int]] = mapped_column(ForeignKey("coding_questions.id", ondelete="CASCADE"), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    marks: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    test: Mapped["Test"] = relationship(back_populates="test_questions")
    question: Mapped[Optional["Question"]] = relationship(back_populates="test_questions")
    coding_question: Mapped[Optional["CodingQuestion"]] = relationship(back_populates="test_questions")


class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[AttemptStatus] = mapped_column(SAEnum(AttemptStatus), default=AttemptStatus.IN_PROGRESS)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    question_order: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Randomized order stored server-side
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    test: Mapped["Test"] = relationship(back_populates="attempts")
    answers: Mapped[List["TestAnswer"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")
    proctoring_events: Mapped[List["ProctoringEvent"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class TestAnswer(Base):
    __tablename__ = "test_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[Optional[int]] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=True)
    selected_option_id: Mapped[Optional[int]] = mapped_column(ForeignKey("question_options.id"), nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    marks_awarded: Mapped[float] = mapped_column(Float, default=0.0)
    time_taken_seconds: Mapped[int] = mapped_column(Integer, default=0)
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    attempt: Mapped["TestAttempt"] = relationship(back_populates="answers")


class ProctoringEvent(Base):
    __tablename__ = "proctoring_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # tab_switch, window_blur, copy, paste, etc.
    severity: Mapped[str] = mapped_column(String(20), default="LOW")  # LOW, MEDIUM, HIGH
    description: Mapped[Optional[str]] = mapped_column(Text)
    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    attempt: Mapped["TestAttempt"] = relationship(back_populates="proctoring_events")
