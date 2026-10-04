"""
User, Role, Student & Trainer profile models.
"""
from __future__ import annotations
import enum
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, DateTime, Text, ForeignKey,
    Enum as SAEnum, Integer, Float
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    TRAINER = "TRAINER"
    ADMIN = "ADMIN"


def now_utc():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    student_profile: Mapped[Optional["StudentProfile"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    trainer_profile: Mapped[Optional["TrainerProfile"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    college: Mapped[Optional[str]] = mapped_column(String(255))
    department: Mapped[Optional[str]] = mapped_column(String(100))
    graduation_year: Mapped[Optional[int]] = mapped_column(Integer)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    total_score: Mapped[float] = mapped_column(Float, default=0.0)
    aptitude_score: Mapped[float] = mapped_column(Float, default=0.0)
    coding_score: Mapped[float] = mapped_column(Float, default=0.0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_active: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="student_profile")
    batch_memberships: Mapped[List["BatchMembership"]] = relationship(back_populates="student")
    topic_progress: Mapped[List["TopicProgress"]] = relationship(back_populates="student", cascade="all, delete-orphan")


class TrainerProfile(Base):
    __tablename__ = "trainer_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    specialization: Mapped[Optional[str]] = mapped_column(String(255))
    experience_years: Mapped[Optional[int]] = mapped_column(Integer)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="trainer_profile")
    batches: Mapped[List["Batch"]] = relationship(back_populates="trainer")


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainer_profiles.id", ondelete="CASCADE"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    # Relationships
    trainer: Mapped["TrainerProfile"] = relationship(back_populates="batches")
    members: Mapped[List["BatchMembership"]] = relationship(back_populates="batch", cascade="all, delete-orphan")


class BatchMembership(Base):
    __tablename__ = "batch_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    batch: Mapped["Batch"] = relationship(back_populates="members")
    student: Mapped["StudentProfile"] = relationship(back_populates="batch_memberships")


class TopicProgress(Base):
    __tablename__ = "topic_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    lessons_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_lessons: Mapped[int] = mapped_column(Integer, default=0)
    questions_attempted: Mapped[int] = mapped_column(Integer, default=0)
    questions_correct: Mapped[int] = mapped_column(Integer, default=0)
    skill_rating: Mapped[float] = mapped_column(Float, default=1000.0)  # Elo-style
    irt_ability: Mapped[float] = mapped_column(Float, default=0.0)  # Standardized IRT theta [-3.0 to +3.0]
    recent_accuracy: Mapped[float] = mapped_column(Float, default=0.5)  # Exponential moving average
    avg_response_time_seconds: Mapped[float] = mapped_column(Float, default=30.0)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_practiced: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    # Relationships
    student: Mapped["StudentProfile"] = relationship(back_populates="topic_progress")
    topic: Mapped["Topic"] = relationship(back_populates="student_progress")
