"""
Coding practice, evaluation, and assessment routes for students.
Provides Monaco-compatible execution, submission scoring, and authoritative server-side timing.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import random
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.api.deps import get_student_profile
from app.models.user import StudentProfile
from app.models.coding import CodingQuestion, TestCase, CodeSubmission, SubmissionVerdict
from app.models.test import Test, TestAttempt, TestQuestion, AttemptStatus, TestType, ProctoringEvent
from app.models.content import Topic
from app.schemas.coding import (
    CodingQuestionSummary,
    CodingQuestionDetail,
    TestCaseOut,
    CodeRunRequest,
    CodeRunResponse,
    CodeSubmitRequest,
    CodeSubmissionOut,
    TestCaseExecutionResult,
    CodingAssessmentDetailOut,
    CodingAssessmentQuestionOut,
)
from app.services.judge0 import judge0_service
from app.services.scoring import calculate_and_sync_student_scores
import logging

router = APIRouter(prefix="/students/coding", tags=["Student Coding"])
logger = logging.getLogger(__name__)


def now_utc():
    return datetime.now(timezone.utc)


# ────────────────────────────── Questions Catalog ──────────────────────────────

@router.get("/questions", response_model=List[CodingQuestionSummary])
async def list_coding_questions(
    difficulty: Optional[str] = None,
    topic_id: Optional[int] = None,
    search: Optional[str] = None,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """List available coding practice questions with summary stats."""
    query = (
        select(CodingQuestion)
        .where(CodingQuestion.is_active == True)
        .options(selectinload(CodingQuestion.topic))
    )

    if difficulty:
        query = query.where(CodingQuestion.difficulty == difficulty.upper())
    if topic_id:
        query = query.where(CodingQuestion.topic_id == topic_id)
    if search:
        search_fmt = f"%{search}%"
        query = query.where(
            or_(
                CodingQuestion.title.ilike(search_fmt),
                CodingQuestion.problem_statement.ilike(search_fmt)
            )
        )

    result = await db.execute(query.order_by(CodingQuestion.id))
    questions = result.scalars().all()

    out = []
    for q in questions:
        acc_rate = (q.accept_count / q.attempt_count * 100) if q.attempt_count > 0 else None
        out.append(
            CodingQuestionSummary(
                id=q.id,
                title=q.title,
                slug=q.slug,
                difficulty=q.difficulty,
                topic_id=q.topic_id,
                topic_name=q.topic.name if q.topic else None,
                marks=q.marks or 10,
                tags=q.tags or [],
                attempt_count=q.attempt_count,
                accept_count=q.accept_count,
                acceptance_rate=round(acc_rate, 1) if acc_rate is not None else None,
                supported_languages=q.supported_languages or ["python", "javascript", "cpp", "java"],
            )
        )
    return out


@router.get("/questions/{id_or_slug}", response_model=CodingQuestionDetail)
async def get_coding_question_detail(
    id_or_slug: str,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed coding question with sample test cases.
    CRITICAL SECURITY: Hidden test cases are completely omitted from this response.
    """
    query = (
        select(CodingQuestion)
        .where(CodingQuestion.is_active == True)
        .options(selectinload(CodingQuestion.topic), selectinload(CodingQuestion.test_cases))
    )
    if id_or_slug.isdigit():
        query = query.where(CodingQuestion.id == int(id_or_slug))
    else:
        query = query.where(CodingQuestion.slug == id_or_slug)

    res = await db.execute(query)
    q = res.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Coding question not found")

    # Filter to only sample/public test cases
    sample_cases = [
        TestCaseOut(
            id=tc.id,
            is_sample=True,
            order_index=tc.order_index,
            input=tc.input,
            expected_output=tc.expected_output,
        )
        for tc in q.test_cases
        if tc.is_sample
    ]

    return CodingQuestionDetail(
        id=q.id,
        title=q.title,
        slug=q.slug,
        difficulty=q.difficulty,
        topic_id=q.topic_id,
        topic_name=q.topic.name if q.topic else None,
        problem_statement=q.problem_statement,
        constraints=q.constraints,
        input_format=q.input_format,
        output_format=q.output_format,
        examples=q.examples or [],
        explanation=q.explanation,
        supported_languages=q.supported_languages or ["python", "javascript", "cpp", "java"],
        time_limit_ms=q.time_limit_ms,
        memory_limit_mb=q.memory_limit_mb,
        marks=q.marks or 10,
        tags=q.tags or [],
        attempt_count=q.attempt_count,
        accept_count=q.accept_count,
        sample_test_cases=sample_cases,
    )


# ────────────────────────────── Run Code (Sample Only) ──────────────────────────────

@router.post("/questions/{question_id}/run", response_model=CodeRunResponse)
async def run_sample_code(
    question_id: int,
    payload: CodeRunRequest,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Executes student code strictly against SAMPLE/PUBLIC test cases.
    Does not score or record submission.
    """
    res = await db.execute(
        select(CodingQuestion)
        .where(CodingQuestion.id == question_id)
        .options(selectinload(CodingQuestion.test_cases))
    )
    q = res.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Coding question not found")

    sample_cases = [tc for tc in q.test_cases if tc.is_sample]
    if not sample_cases:
        sample_cases = q.test_cases[:1]  # fallback if no sample marked

    result = await judge0_service.evaluate_test_cases(
        source_code=payload.source_code,
        language=payload.language,
        test_cases=sample_cases,
        is_submission=False,
        total_marks=float(q.marks or 10),
    )

    tc_results = [
        TestCaseExecutionResult(
            test_case_id=r.test_case_id,
            is_sample=r.is_sample,
            status=r.status,
            passed=r.passed,
            runtime_ms=r.runtime_ms,
            memory_kb=r.memory_kb,
            stdout=r.stdout,
            stderr=r.stderr,
            compile_output=r.compile_output,
            input=r.input,
            expected_output=r.expected_output,
        )
        for r in result.test_results
    ]

    return CodeRunResponse(
        verdict=result.verdict,
        total_tests=result.total_tests,
        passed_tests=result.passed_tests,
        execution_time_ms=result.execution_time_ms,
        memory_kb=result.memory_kb,
        compile_output=result.compile_output,
        stdout=result.stdout,
        stderr=result.stderr,
        test_results=tc_results,
    )


# ────────────────────────────── Submit Code (Public + Hidden) ──────────────────────────────

@router.post("/questions/{question_id}/submit", response_model=CodeSubmissionOut)
async def submit_code(
    question_id: int,
    payload: CodeSubmitRequest,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluates student code against ALL test cases (sample + hidden).
    Calculates final score, records persistent CodeSubmission, and updates student stats.
    CRITICAL: Hidden test inputs/outputs are never returned in client response.
    """
    res = await db.execute(
        select(CodingQuestion)
        .where(CodingQuestion.id == question_id)
        .options(selectinload(CodingQuestion.test_cases))
    )
    q = res.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Coding question not found")

    # If linked to an assessment attempt, validate server-side timing
    attempt: Optional[TestAttempt] = None
    question_max_marks = float(q.marks or 10)
    if payload.attempt_id:
        att_res = await db.execute(
            select(TestAttempt)
            .where(TestAttempt.id == payload.attempt_id)
            .where(TestAttempt.student_id == profile.id)
            .options(selectinload(TestAttempt.test))
        )
        attempt = att_res.scalar_one_or_none()
        if not attempt:
            raise HTTPException(status_code=403, detail="Invalid assessment attempt or access denied")

        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise HTTPException(status_code=400, detail=f"Assessment is {attempt.status.value}; submissions closed")

        if attempt.expires_at and now_utc() > attempt.expires_at:
            attempt.status = AttemptStatus.TIMED_OUT
            attempt.submitted_at = attempt.expires_at
            await db.commit()
            raise HTTPException(status_code=400, detail="Assessment time has expired")

        # In assessment context, scale question points to uniform assessment fraction (e.g. 100 / 20 = 5.0)
        num_questions = len(attempt.question_order) if attempt.question_order else 20
        total_test_marks = float(attempt.test.total_marks or 100) if attempt.test else 100.0
        question_max_marks = round(total_test_marks / max(1, num_questions), 1)

    # Run evaluation against all test cases
    eval_result = await judge0_service.evaluate_test_cases(
        source_code=payload.source_code,
        language=payload.language,
        test_cases=q.test_cases,
        is_submission=True,
        total_marks=question_max_marks,
    )

    verdict_enum = getattr(SubmissionVerdict, eval_result.verdict, SubmissionVerdict.RUNTIME_ERROR)

    # Persist submission record
    sub = CodeSubmission(
        student_id=profile.id,
        coding_question_id=q.id,
        attempt_id=payload.attempt_id,
        source_code=payload.source_code,
        language=payload.language,
        verdict=verdict_enum,
        stdout=eval_result.stdout,
        stderr=eval_result.stderr,
        compile_output=eval_result.compile_output,
        runtime_ms=eval_result.execution_time_ms,
        memory_kb=eval_result.memory_kb,
        test_cases_passed=eval_result.passed_tests,
        test_cases_total=eval_result.total_tests,
        score=eval_result.score,
        is_final_submission=True,
        result_details=[
            {
                "test_case_id": r.test_case_id,
                "is_sample": r.is_sample,
                "passed": r.passed,
                "status": r.status,
                "runtime_ms": r.runtime_ms,
            }
            for r in eval_result.test_results
        ],
    )
    db.add(sub)

    # Update question stats
    q.attempt_count = (q.attempt_count or 0) + 1
    if eval_result.verdict == "ACCEPTED":
        q.accept_count = (q.accept_count or 0) + 1

    # Update student profile scoring dynamically with authoritative scoring engine (for standalone practice mode)
    if not payload.attempt_id:
        await calculate_and_sync_student_scores(db, profile)
    else:
        await db.commit()
    await db.refresh(sub)

    tc_results = [
        TestCaseExecutionResult(
            test_case_id=r.test_case_id,
            is_sample=r.is_sample,
            status=r.status,
            passed=r.passed,
            runtime_ms=r.runtime_ms,
            memory_kb=r.memory_kb,
            stdout=r.stdout,
            stderr=r.stderr,
            compile_output=r.compile_output,
            input=r.input,              # Redacted (None) for hidden tests
            expected_output=r.expected_output,  # Redacted (None) for hidden tests
        )
        for r in eval_result.test_results
    ]

    return CodeSubmissionOut(
        id=sub.id,
        student_id=sub.student_id,
        coding_question_id=sub.coding_question_id,
        question_title=q.title,
        attempt_id=sub.attempt_id,
        language=sub.language,
        source_code=sub.source_code,
        verdict=sub.verdict.value,
        score=sub.score,
        test_cases_passed=sub.test_cases_passed,
        test_cases_total=sub.test_cases_total,
        runtime_ms=sub.runtime_ms,
        memory_kb=sub.memory_kb,
        compile_output=sub.compile_output,
        submitted_at=sub.submitted_at,
        test_results=tc_results,
    )


# ────────────────────────────── Submissions History ──────────────────────────────

@router.get("/submissions", response_model=List[CodeSubmissionOut])
async def list_student_submissions(
    question_id: Optional[int] = None,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """Get the current student's previous submissions with strict ownership isolation."""
    query = (
        select(CodeSubmission)
        .where(CodeSubmission.student_id == profile.id)
        .options(selectinload(CodeSubmission.coding_question))
        .order_by(CodeSubmission.submitted_at.desc())
    )
    if question_id:
        query = query.where(CodeSubmission.coding_question_id == question_id)

    res = await db.execute(query)
    subs = res.scalars().all()

    return [
        CodeSubmissionOut(
            id=s.id,
            student_id=s.student_id,
            coding_question_id=s.coding_question_id,
            question_title=s.coding_question.title if s.coding_question else "Coding Problem",
            attempt_id=s.attempt_id,
            language=s.language,
            source_code=s.source_code,
            verdict=s.verdict.value,
            score=s.score,
            test_cases_passed=s.test_cases_passed,
            test_cases_total=s.test_cases_total,
            runtime_ms=s.runtime_ms,
            memory_kb=s.memory_kb,
            compile_output=s.compile_output,
            submitted_at=s.submitted_at,
            test_results=[],
        )
        for s in subs
    ]


@router.get("/submissions/{submission_id}", response_model=CodeSubmissionOut)
async def get_submission_detail(
    submission_id: int,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific submission.
    SECURITY: Rejects access if the submission belongs to another student.
    """
    res = await db.execute(
        select(CodeSubmission)
        .where(CodeSubmission.id == submission_id)
        .options(selectinload(CodeSubmission.coding_question))
    )
    sub = res.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    if sub.student_id != profile.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to another student's submission")

    return CodeSubmissionOut(
        id=sub.id,
        student_id=sub.student_id,
        coding_question_id=sub.coding_question_id,
        question_title=sub.coding_question.title if sub.coding_question else "Coding Problem",
        attempt_id=sub.attempt_id,
        language=sub.language,
        source_code=sub.source_code,
        verdict=sub.verdict.value,
        score=sub.score,
        test_cases_passed=sub.test_cases_passed,
        test_cases_total=sub.test_cases_total,
        runtime_ms=sub.runtime_ms,
        memory_kb=sub.memory_kb,
        compile_output=sub.compile_output,
        submitted_at=sub.submitted_at,
        test_results=[],
    )


# ────────────────────────────── Coding Assessments ──────────────────────────────

@router.post("/assessments/{test_id}/start", response_model=CodingAssessmentDetailOut)
async def start_coding_assessment(
    test_id: int,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Start or resume a coding assessment.
    Authoritative server clock sets expires_at = started_at + duration_minutes.
    """
    test_res = await db.execute(
        select(Test)
        .where(Test.id == test_id)
        .where(Test.test_type.in_([TestType.CODING, TestType.MIXED]))
        .options(
            selectinload(Test.test_questions).selectinload(TestQuestion.coding_question).selectinload(CodingQuestion.test_cases)
        )
    )
    test = test_res.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Coding assessment not found")

    # Check for existing active attempt
    att_res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.test_id == test_id)
        .where(TestAttempt.student_id == profile.id)
        .where(TestAttempt.status == AttemptStatus.IN_PROGRESS)
        .order_by(TestAttempt.id.desc())
    )
    attempt = att_res.scalars().first()
    now = now_utc()

    if attempt and attempt.expires_at:
        exp = attempt.expires_at if attempt.expires_at.tzinfo else attempt.expires_at.replace(tzinfo=timezone.utc)
        if now > exp:
            attempt.status = AttemptStatus.TIMED_OUT
            attempt.submitted_at = exp
            await db.commit()
            attempt = None

    if not attempt:
        expires = now + timedelta(minutes=test.duration_minutes)
        attempt = TestAttempt(
            test_id=test.id,
            student_id=profile.id,
            status=AttemptStatus.IN_PROGRESS,
            started_at=now,
            expires_at=expires,
            max_score=float(test.total_marks or 100),
        )
        db.add(attempt)
        await db.flush()

        # Dynamic selection of 20 coding problems: 8 EASY, 8 MEDIUM, 4 HARD (Total = 20)
        # 1. Collect previously attempted / seen coding questions for this student
        past_coding_ids = set()
        sub_res = await db.execute(
            select(CodeSubmission.coding_question_id)
            .where(CodeSubmission.student_id == profile.id)
        )
        for qid in sub_res.scalars().all():
            if qid:
                past_coding_ids.add(qid)

        past_att_res = await db.execute(
            select(TestAttempt.question_order)
            .where(TestAttempt.student_id == profile.id)
            .where(TestAttempt.test_id == test_id)
        )
        for row in past_att_res.scalars().all():
            if row and isinstance(row, list):
                for qid in row:
                    past_coding_ids.add(qid)

        # 2. Query all active coding questions
        all_cqs_res = await db.execute(
            select(CodingQuestion).where(CodingQuestion.is_active == True)
        )
        all_cqs = all_cqs_res.scalars().all()

        easy_pool = [q for q in all_cqs if str(q.difficulty).upper() == "EASY"]
        med_pool = [q for q in all_cqs if str(q.difficulty).upper() == "MEDIUM"]
        hard_pool = [q for q in all_cqs if str(q.difficulty).upper() == "HARD"]

        def pick_k(pool: list, k: int) -> list:
            if not pool:
                return []
            unseen = [q for q in pool if q.id not in past_coding_ids]
            if len(unseen) >= k:
                return random.sample(unseen, k)
            seen = [q for q in pool if q.id in past_coding_ids]
            return list(unseen) + random.sample(seen, min(k - len(unseen), len(seen)))

        # Select 8 EASY, 8 MEDIUM, 4 HARD = 20 problems total
        sel_easy = pick_k(easy_pool, min(8, len(easy_pool)))
        sel_med = pick_k(med_pool, min(8, len(med_pool)))
        sel_hard = pick_k(hard_pool, min(4, len(hard_pool)))

        chosen = sel_easy + sel_med + sel_hard
        # Ensure 20 problems if any pool was short
        if len(chosen) < 20:
            remaining_cqs = [q for q in all_cqs if q not in chosen]
            if remaining_cqs:
                chosen.extend(random.sample(remaining_cqs, min(20 - len(chosen), len(remaining_cqs))))

        attempt.question_order = [q.id for q in chosen]
        await db.commit()
        await db.refresh(attempt)

    # Calculate authoritative remaining time
    remaining = max(0, int((attempt.expires_at - now).total_seconds())) if attempt.expires_at else 0
    is_expired = remaining <= 0

    if is_expired and attempt.status == AttemptStatus.IN_PROGRESS:
        attempt.status = AttemptStatus.TIMED_OUT
        attempt.submitted_at = attempt.expires_at
        await db.commit()

    # Load questions directly from attempt.question_order
    order_ids = attempt.question_order or []
    cqs_res = await db.execute(
        select(CodingQuestion)
        .where(CodingQuestion.id.in_(order_ids))
        .options(selectinload(CodingQuestion.test_cases))
    )
    cq_map = {cq.id: cq for cq in cqs_res.scalars().all()}
    ordered_cqs = [cq_map[qid] for qid in order_ids if qid in cq_map]

    # Fallback to test.test_questions if attempt.question_order was empty
    if not ordered_cqs:
        ordered_cqs = [tq.coding_question for tq in sorted(test.test_questions, key=lambda x: x.order_index) if tq.coding_question]

    # Uniform marks per question (e.g. 100 total marks / 20 questions = 5.0 marks per question)
    per_q_marks = round(float(test.total_marks or 100) / max(1, len(ordered_cqs)), 1)

    questions_out = []
    for cq in ordered_cqs:
        sample_cases = [
            TestCaseOut(
                id=tc.id,
                is_sample=True,
                order_index=tc.order_index,
                input=tc.input,
                expected_output=tc.expected_output,
            )
            for tc in cq.test_cases
            if tc.is_sample
        ]

        # Get latest submission for this question in this attempt
        sub_res = await db.execute(
            select(CodeSubmission)
            .where(CodeSubmission.attempt_id == attempt.id)
            .where(CodeSubmission.coding_question_id == cq.id)
            .order_by(CodeSubmission.submitted_at.desc())
            .limit(1)
        )
        latest_sub = sub_res.scalar_one_or_none()
        user_sub_out = None
        if latest_sub:
            user_sub_out = CodeSubmissionOut(
                id=latest_sub.id,
                student_id=latest_sub.student_id,
                coding_question_id=latest_sub.coding_question_id,
                question_title=cq.title,
                attempt_id=latest_sub.attempt_id,
                language=latest_sub.language,
                source_code=latest_sub.source_code,
                verdict=latest_sub.verdict.value,
                score=latest_sub.score,
                test_cases_passed=latest_sub.test_cases_passed,
                test_cases_total=latest_sub.test_cases_total,
                runtime_ms=latest_sub.runtime_ms,
                memory_kb=latest_sub.memory_kb,
                compile_output=latest_sub.compile_output,
                submitted_at=latest_sub.submitted_at,
                test_results=[],
            )

        marks = int(per_q_marks)

        questions_out.append(
            CodingAssessmentQuestionOut(
                id=cq.id,
                title=cq.title,
                slug=cq.slug,
                difficulty=cq.difficulty,
                marks=marks,
                problem_statement=cq.problem_statement,
                constraints=cq.constraints,
                input_format=cq.input_format,
                output_format=cq.output_format,
                examples=cq.examples or [],
                supported_languages=cq.supported_languages or ["python", "javascript", "cpp", "java"],
                sample_test_cases=sample_cases,
                user_submission=user_sub_out,
            )
        )

    return CodingAssessmentDetailOut(
        test_id=test.id,
        attempt_id=attempt.id,
        title=test.title,
        description=test.description,
        duration_minutes=test.duration_minutes,
        total_marks=test.total_marks,
        passing_marks=test.passing_marks,
        instructions=test.instructions,
        remaining_seconds=remaining,
        is_expired=is_expired,
        started_at=attempt.started_at,
        expires_at=attempt.expires_at,
        questions=questions_out,
    )


@router.post("/assessments/{test_id}/finalize")
async def finalize_coding_assessment(
    test_id: int,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Finalizes assessment attempt, computes cumulative score, and locks further submissions.
    """
    att_res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.test_id == test_id)
        .where(TestAttempt.student_id == profile.id)
        .where(TestAttempt.status == AttemptStatus.IN_PROGRESS)
        .options(selectinload(TestAttempt.test))
    )
    attempt = att_res.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Active assessment attempt not found")

    # Aggregate best scores per coding question in this attempt
    subs_res = await db.execute(
        select(CodeSubmission)
        .where(CodeSubmission.attempt_id == attempt.id)
    )
    subs = subs_res.scalars().all()

    best_question_scores = {}
    for s in subs:
        cq_id = s.coding_question_id
        if cq_id not in best_question_scores or (s.score or 0) > best_question_scores[cq_id]:
            best_question_scores[cq_id] = s.score or 0.0

    max_score = float(attempt.test.total_marks or 100)
    total_score = min(max_score, round(sum(best_question_scores.values()), 1))
    percentage = min(100.0, round((total_score / max_score) * 100, 1)) if max_score > 0 else 0.0

    attempt.score = total_score
    attempt.max_score = max_score
    attempt.percentage = percentage
    attempt.submitted_at = now_utc()
    attempt.status = AttemptStatus.GRADED

    # Commit attempt status first so scoring engine includes this newly graded attempt
    await db.commit()

    # Update student profile scores dynamically with authoritative scoring engine
    await calculate_and_sync_student_scores(db, profile)

    return {
        "attempt_id": attempt.id,
        "status": attempt.status.value,
        "score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "is_passed": percentage >= (attempt.test.passing_marks or 40),
    }


@router.get("/assessments/{test_id}/time")
async def get_assessment_server_time(
    test_id: int,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Authoritative server clock remaining time check.
    Prevents browser timer manipulation.
    """
    att_res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.test_id == test_id)
        .where(TestAttempt.student_id == profile.id)
        .where(TestAttempt.status == AttemptStatus.IN_PROGRESS)
        .order_by(TestAttempt.id.desc())
    )
    attempt = att_res.scalars().first()
    if not attempt:
        raise HTTPException(status_code=404, detail="No active attempt found")

    now = now_utc()
    remaining = max(0, int((attempt.expires_at - now).total_seconds())) if attempt.expires_at else 0
    is_expired = remaining <= 0

    if is_expired and attempt.status == AttemptStatus.IN_PROGRESS:
        attempt.status = AttemptStatus.TIMED_OUT
        attempt.submitted_at = attempt.expires_at
        await db.commit()

    return {
        "attempt_id": attempt.id,
        "remaining_seconds": remaining,
        "is_expired": is_expired,
        "server_time": now.isoformat(),
        "expires_at": attempt.expires_at.isoformat() if attempt.expires_at else None,
    }
