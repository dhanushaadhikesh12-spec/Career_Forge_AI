"""
Analytics records for ML processing.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
)
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class AnalyticsRecord(Base):
    """Denormalized analytics snapshot — updated after each test/practice session."""
    __tablename__ = "analytics_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # test_completed, practice_session, etc.
    test_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tests.id", ondelete="SET NULL"), nullable=True)
    topic_id: Mapped[Optional[int]] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    event_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, index=True)


class PlacementReadiness(Base):
    """ML-computed placement readiness score (updated periodically)."""
    __tablename__ = "placement_readiness"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id", ondelete="CASCADE"), unique=True, nullable=False)
    readiness_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    aptitude_component: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    coding_component: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    consistency_component: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_trained: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    computed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
