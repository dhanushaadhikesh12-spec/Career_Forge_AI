"""
Subjects, Topics, Lessons, Questions, and Practice content models.
"""
from __future__ import annotations
import enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, Enum as SAEnum, JSON, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class DifficultyLevel(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class SubjectCategory(str, enum.Enum):
    APTITUDE = "APTITUDE"
    PROGRAMMING = "PROGRAMMING"


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[SubjectCategory] = mapped_column(SAEnum(SubjectCategory), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon: Mapped[Optional[str]] = mapped_column(String(100))
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    topics: Mapped[List["Topic"]] = relationship(back_populates="subject", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    subject: Mapped["Subject"] = relationship(back_populates="topics")
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="topic", cascade="all, delete-orphan")
    questions: Mapped[List["Question"]] = relationship(back_populates="topic")
    student_progress: Mapped[List["TopicProgress"]] = relationship(back_populates="topic")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    examples: Mapped[Optional[str]] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=10)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    topic: Mapped["Topic"] = relationship(back_populates="lessons")
    completions: Mapped[List["LessonCompletion"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")


class LessonCompletion(Base):
    __tablename__ = "lesson_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    lesson: Mapped["Lesson"] = relationship(back_populates="completions")


class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    TRUE_FALSE = "TRUE_FALSE"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(SAEnum(QuestionType), default=QuestionType.MCQ)
    difficulty: Mapped[DifficultyLevel] = mapped_column(SAEnum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    points: Mapped[int] = mapped_column(Integer, default=1)
    irt_difficulty: Mapped[float] = mapped_column(Float, default=0.0)  # Item Response Theory param
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    topic: Mapped[Optional["Topic"]] = relationship(back_populates="questions")
    options: Mapped[List["QuestionOption"]] = relationship(
        back_populates="question", cascade="all, delete-orphan", order_by="QuestionOption.order_index"
    )
    test_questions: Mapped[List["TestQuestion"]] = relationship(back_populates="question")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    question: Mapped["Question"] = relationship(back_populates="options")


class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    selected_option_id: Mapped[Optional[int]] = mapped_column(ForeignKey("question_options.id"), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    time_taken_seconds: Mapped[int] = mapped_column(Integer, default=0)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class StudentQuestionHistory(Base):
    __tablename__ = "student_question_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    times_seen: Mapped[int] = mapped_column(Integer, default=1)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)
    times_incorrect: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("student_id", "question_id", name="uq_student_question_history"),
    )

