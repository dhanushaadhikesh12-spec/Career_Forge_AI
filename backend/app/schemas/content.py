"""
Pydantic schemas for content: subjects, topics, lessons, questions, practice.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.models.content import DifficultyLevel, SubjectCategory, QuestionType


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: SubjectCategory
    description: Optional[str]
    icon: Optional[str]
    order_index: int


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject_id: int
    name: str
    description: Optional[str]
    order_index: int
    total_lessons: Optional[int] = 0
    total_questions: Optional[int] = 0


class LessonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    topic_id: int
    title: str
    content: str
    examples: Optional[str]
    order_index: int
    estimated_minutes: int


class QuestionOptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    text: str
    order_index: int
    # is_correct is NOT included by default — only sent after submission


class QuestionOptionWithAnswer(QuestionOptionOut):
    is_correct: bool


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    topic_id: Optional[int]
    text: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    explanation: Optional[str]
    points: int
    options: List[QuestionOptionOut]


class QuestionWithAnswer(QuestionOut):
    options: List[QuestionOptionWithAnswer]


class PracticeSessionRequest(BaseModel):
    topic_id: int
    difficulty: Optional[DifficultyLevel] = None
    count: int = Field(default=10, ge=1, le=50)


class PracticeAnswerSubmit(BaseModel):
    question_id: int
    selected_option_id: int
    time_taken_seconds: int = Field(default=0, ge=0)


class PracticeAnswerResult(BaseModel):
    question_id: int
    selected_option_id: int
    is_correct: bool
    correct_option_id: int
    explanation: Optional[str] = None
    points_earned: int = 0
    old_skill_rating: Optional[float] = None
    new_skill_rating: Optional[float] = None
    skill_delta: Optional[float] = None
    old_theta: Optional[float] = None
    new_theta: Optional[float] = None
    streak: Optional[int] = None
    topic_accuracy: Optional[float] = None
    adaptive_message: Optional[str] = None
    recommended_next_difficulty: Optional[str] = None


class TopicProgressOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    topic_id: int
    topic_name: Optional[str] = None
    lessons_completed: int = 0
    total_lessons: int = 0
    questions_attempted: int = 0
    questions_correct: int = 0
    skill_rating: float = 1000.0
    irt_ability: Optional[float] = 0.0
    recent_accuracy: Optional[float] = 0.5
    avg_response_time_seconds: Optional[float] = 30.0
    streak: Optional[int] = 0
    accuracy: Optional[float] = None
    last_practiced: Optional[datetime] = None
