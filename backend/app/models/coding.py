"""
Coding questions, test cases, and code submissions.
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


class SubmissionVerdict(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    WRONG_ANSWER = "WRONG_ANSWER"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class CodingQuestion(Base):
    __tablename__ = "coding_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    constraints: Mapped[Optional[str]] = mapped_column(Text)
    input_format: Mapped[Optional[str]] = mapped_column(Text)
    output_format: Mapped[Optional[str]] = mapped_column(Text)
    examples: Mapped[Optional[list]] = mapped_column(JSON)  # [{input, output, explanation}]
    difficulty: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    supported_languages: Mapped[list] = mapped_column(JSON, default=list)  # ["python", "java", "cpp", "javascript"]
    time_limit_ms: Mapped[int] = mapped_column(Integer, default=2000)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=256)
    marks: Mapped[int] = mapped_column(Integer, default=10)
    tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    topic_id: Mapped[Optional[int]] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    accept_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    topic: Mapped[Optional["Topic"]] = relationship()
    test_cases: Mapped[List["TestCase"]] = relationship(back_populates="coding_question", cascade="all, delete-orphan")
    test_questions: Mapped[List["TestQuestion"]] = relationship(back_populates="coding_question")
    submissions: Mapped[List["CodeSubmission"]] = relationship(back_populates="coding_question")


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    coding_question_id: Mapped[int] = mapped_column(ForeignKey("coding_questions.id", ondelete="CASCADE"), nullable=False)
    input: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)  # Sample = visible to student
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    coding_question: Mapped["CodingQuestion"] = relationship(back_populates="test_cases")


class CodeSubmission(Base):
    __tablename__ = "code_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    coding_question_id: Mapped[int] = mapped_column(ForeignKey("coding_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_id: Mapped[Optional[int]] = mapped_column(ForeignKey("test_attempts.id", ondelete="SET NULL"), nullable=True)
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    verdict: Mapped[SubmissionVerdict] = mapped_column(SAEnum(SubmissionVerdict), default=SubmissionVerdict.PENDING)
    judge0_token: Mapped[Optional[str]] = mapped_column(String(255))
    stdout: Mapped[Optional[str]] = mapped_column(Text)
    stderr: Mapped[Optional[str]] = mapped_column(Text)
    compile_output: Mapped[Optional[str]] = mapped_column(Text)
    runtime_ms: Mapped[Optional[float]] = mapped_column(Float)
    memory_kb: Mapped[Optional[float]] = mapped_column(Float)
    test_cases_passed: Mapped[int] = mapped_column(Integer, default=0)
    test_cases_total: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    is_final_submission: Mapped[bool] = mapped_column(Boolean, default=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    result_details: Mapped[Optional[list]] = mapped_column(JSON)  # Per-test-case results

    # Relationships
    coding_question: Mapped["CodingQuestion"] = relationship(back_populates="submissions")
