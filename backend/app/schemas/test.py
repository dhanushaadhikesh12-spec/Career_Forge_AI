"""
Pydantic schemas for tests and test attempts.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field
from app.models.test import TestType, TestStatus, AttemptStatus


class TestCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    test_type: TestType = TestType.APTITUDE
    batch_id: Optional[int] = None
    duration_minutes: int = Field(default=60, ge=5, le=360)
    total_marks: int = Field(default=100, ge=1)
    passing_marks: int = Field(default=40, ge=0)
    instructions: Optional[str] = None
    randomize_questions: bool = True
    show_results_immediately: bool = False
    question_ids: List[int] = []
    scheduled_at: Optional[datetime] = None


class TestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    test_type: TestType
    status: TestStatus
    batch_id: Optional[int]
    duration_minutes: int
    total_marks: int
    passing_marks: int
    instructions: Optional[str]
    randomize_questions: bool
    show_results_immediately: bool
    scheduled_at: Optional[datetime]
    created_at: datetime
    question_count: Optional[int] = 0


class TestStartResponse(BaseModel):
    attempt_id: int
    test_id: int
    expires_at: datetime
    questions: List[Any]  # Questions without answers


class AnswerSubmit(BaseModel):
    question_id: int
    selected_option_id: int
    time_taken_seconds: int = Field(default=0, ge=0)


class TestSubmitRequest(BaseModel):
    attempt_id: int
    answers: List[AnswerSubmit]


class TestAttemptResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    test_id: int
    student_id: int
    status: AttemptStatus
    started_at: datetime
    submitted_at: Optional[datetime]
    score: Optional[float]
    max_score: Optional[float]
    percentage: Optional[float]
    passed: Optional[bool] = None


class TestAttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    test_id: int
    status: AttemptStatus
    started_at: datetime
    submitted_at: Optional[datetime]
    score: Optional[float]
    percentage: Optional[float]
    test: Optional[TestOut]


class ProctoringEventCreate(BaseModel):
    attempt_id: int
    event_type: str = Field(..., max_length=100)
    severity: str = "LOW"
    description: Optional[str] = None
    event_metadata: Optional[dict] = None


class ProctoringEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_type: str
    severity: str
    description: Optional[str]
    occurred_at: datetime
