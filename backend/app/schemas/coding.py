"""
Pydantic schemas for coding questions, test cases, and code execution.
"""
from __future__ import annotations
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TestCaseOut(BaseModel):
    id: int
    is_sample: bool
    order_index: int
    # Hidden test case input/output must remain None for student responses
    input: Optional[str] = None
    expected_output: Optional[str] = None


class CodingQuestionSummary(BaseModel):
    id: int
    title: str
    slug: str
    difficulty: str
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    marks: int = 10
    tags: Optional[List[str]] = []
    attempt_count: int = 0
    accept_count: int = 0
    acceptance_rate: Optional[float] = None
    supported_languages: List[str] = ["python", "javascript", "cpp", "java"]


class CodingQuestionDetail(BaseModel):
    id: int
    title: str
    slug: str
    difficulty: str
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    problem_statement: str
    constraints: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    examples: Optional[List[dict]] = None
    explanation: Optional[str] = None
    supported_languages: List[str] = ["python", "javascript", "cpp", "java"]
    time_limit_ms: int = 2000
    memory_limit_mb: int = 256
    marks: int = 10
    tags: Optional[List[str]] = []
    attempt_count: int = 0
    accept_count: int = 0
    sample_test_cases: List[TestCaseOut] = []


class CodeRunRequest(BaseModel):
    source_code: str = Field(..., min_length=1)
    language: str = Field(..., min_length=1)


class TestCaseExecutionResult(BaseModel):
    test_case_id: int
    is_sample: bool
    status: str
    passed: bool
    runtime_ms: float
    memory_kb: float
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None
    input: Optional[str] = None
    expected_output: Optional[str] = None


class CodeRunResponse(BaseModel):
    verdict: str
    total_tests: int
    passed_tests: int
    execution_time_ms: float
    memory_kb: float
    compile_output: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    test_results: List[TestCaseExecutionResult] = []


class CodeSubmitRequest(BaseModel):
    source_code: str = Field(..., min_length=1)
    language: str = Field(..., min_length=1)
    attempt_id: Optional[int] = None  # Assessment test attempt if part of an active test


class CodeSubmissionOut(BaseModel):
    id: int
    student_id: int
    coding_question_id: int
    question_title: Optional[str] = None
    attempt_id: Optional[int] = None
    language: str
    source_code: str
    verdict: str
    score: float
    test_cases_passed: int
    test_cases_total: int
    runtime_ms: Optional[float] = None
    memory_kb: Optional[float] = None
    compile_output: Optional[str] = None
    submitted_at: datetime
    test_results: List[TestCaseExecutionResult] = []


class CodingAssessmentQuestionOut(BaseModel):
    id: int
    title: str
    slug: str
    difficulty: str
    marks: int
    problem_statement: str
    constraints: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    examples: Optional[List[dict]] = None
    supported_languages: List[str] = ["python", "javascript", "cpp", "java"]
    sample_test_cases: List[TestCaseOut] = []
    user_submission: Optional[CodeSubmissionOut] = None


class CodingAssessmentDetailOut(BaseModel):
    test_id: int
    attempt_id: int
    title: str
    description: Optional[str] = None
    duration_minutes: int
    total_marks: int
    passing_marks: int
    instructions: Optional[str] = None
    remaining_seconds: int
    is_expired: bool
    started_at: datetime
    expires_at: Optional[datetime] = None
    questions: List[CodingAssessmentQuestionOut] = []
