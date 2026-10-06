"""
Automated Test Suite for Trainer AI Student-Level Intelligence Upgrade.

Covers:
1. Placement readiness returns student names and metrics, not count-only.
2. Weak DSA queries return student names and weak topics.
3. At-risk queries return student names, risk levels, and reasons.
4. Individual student performance resolves student name without leaking sensitive data.
5. Batch performance returns aggregate metrics and individual student breakdown.
6. Server-side RBAC strictly blocks cross-batch/unauthorized access.
7. Ambiguous student names return disambiguation prompt instead of guessing.
8. Top performers query returns actual student names ranked by metric.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.db.database import AsyncSessionLocal
from app.models.user import TrainerProfile, StudentProfile, Batch, User
from app.services.ai.tools import (
    build_trainer_context,
    resolve_authorized_student,
    tool_get_placement_readiness,
    tool_get_weak_students,
    tool_get_at_risk_students,
    tool_get_student_performance,
    tool_get_batch_summary,
    tool_get_top_students,
)
from app.services.ai.assistant import process_trainer_query
from app.services.ai.provider import MockLLMProvider
from app.services.ai.intent_classifier import classify_intent, QueryIntent


# ─────────────────────────────────────────────────────────────────────────────
# 1. Intent Detection Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_intent_classification_student_queries():
    """Verifies that student-level queries are accurately identified as DATA_QUERY."""
    student_queries = [
        "Who is placement ready?",
        "Which students are at risk?",
        "Who is weak in DSA?",
        "Who are the top 5 coding performers?",
        "Show me students who need improvement.",
        "How is Rahul performing?",
        "How is Rahul Kumar performing?",
        "How is my batch performing?",
        "Who has the highest aptitude score?",
        "Which students are weak in arrays?",
        "Who performed poorly in the latest assessment?",
    ]
    for q in student_queries:
        intent = classify_intent(q)
        assert intent == QueryIntent.DATA_QUERY, f"Query '{q}' should be classified as DATA_QUERY, got {intent}"

    conversational_queries = [
        "Hello",
        "Hi there",
        "What is Elo rating?",
        "How does binary search work?",
        "Good morning",
    ]
    for q in conversational_queries:
        intent = classify_intent(q)
        assert intent == QueryIntent.CONVERSATIONAL, f"Query '{q}' should be classified as CONVERSATIONAL, got {intent}"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Placement Readiness: Names + Metrics (Not Count Only)
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_placement_readiness_returns_student_names():
    """Verifies that asking 'Who are placement ready?' returns actual student names."""
    async with AsyncSessionLocal() as db:
        t_res = await db.execute(select(TrainerProfile).where(TrainerProfile.id == 1))
        trainer = t_res.scalar_one()
        ctx = await build_trainer_context(db, trainer)

        # 1. Direct tool execution
        tool_res = await tool_get_placement_readiness(ctx, db)
        assert "placement_ready_students" in tool_res
        assert tool_res["placement_ready_count"] >= 1
        ready_students = tool_res["placement_ready_students"]
        assert len(ready_students) >= 1

        first = ready_students[0]
        assert "student_name" in first
        assert "readiness_score" in first
        assert "aptitude_score" in first
        assert "coding_score" in first
        assert first["status"] == "Placement Ready"

        # Verify not count-only
        names = [s["student_name"] for s in ready_students]
        assert any("Rahul" in n or "Alice" in n or "Priya" in n for n in names)

        # 2. Pipeline execution with Mock LLM
        mock_provider = MockLLMProvider()
        resp = await process_trainer_query(
            query="Who are placement ready?",
            trainer_profile=trainer,
            db=db,
            provider=mock_provider,
        )
        assert resp.status == "SUCCESS"
        assert resp.tool_called == "get_placement_readiness"
        # Reply must contain names, not just count
        assert any(n in resp.reply for n in names)
        assert "Placement-ready students" in resp.reply


# ─────────────────────────────────────────────────────────────────────────────
# 3. Weak DSA Query: Names + Topics + Accuracy
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_weak_dsa_returns_student_names_and_topics():
    """Verifies that asking 'Who is weak in DSA?' returns names and weak topics."""
    async with AsyncSessionLocal() as db:
        t_res = await db.execute(select(TrainerProfile).where(TrainerProfile.id == 1))
        trainer = t_res.scalar_one()
        ctx = await build_trainer_context(db, trainer)

        tool_res = await tool_get_weak_students(ctx, db, topic="DSA")
        assert "weak_students" in tool_res
        assert len(tool_res["weak_students"]) >= 1

        weak = tool_res["weak_students"]
        for s in weak:
            assert "student_name" in s
            assert "topic_accuracy" in s
            assert "weak_topics" in s

        # Verify through full pipeline
        mock_provider = MockLLMProvider()
        resp = await process_trainer_query(
            query="Who is weak in DSA?",
            trainer_profile=trainer,
            db=db,
            provider=mock_provider,
        )
        assert resp.status == "SUCCESS"
        assert resp.tool_called == "get_weak_students"
        assert len(resp.reply) > 0
        assert any(s["student_name"] in resp.reply for s in weak)


# ─────────────────────────────────────────────────────────────────────────────
# 4. At-Risk Query: Names + Risk Level + Reasons
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_at_risk_students_returns_names_and_reasons():
    """Verifies that asking 'Which students are at risk?' returns names and risk factors."""
    async with AsyncSessionLocal() as db:
        t_res = await db.execute(select(TrainerProfile).where(TrainerProfile.id == 1))
        trainer = t_res.scalar_one()
        ctx = await build_trainer_context(db, trainer)

        tool_res = await tool_get_at_risk_students(ctx, db)
        assert "at_risk_students" in tool_res
        at_risk = tool_res["at_risk_students"]
        assert len(at_risk) >= 1

        for s in at_risk:
            assert "student_name" in s
            assert "risk_level" in s
            assert "readiness_score" in s
            assert "main_reason" in s
            assert "recommended_action" in s

        mock_provider = MockLLMProvider()
        resp = await process_trainer_query(
            query="Which students are at risk?",
            trainer_profile=trainer,
            db=db,
            provider=mock_provider,
        )
        assert resp.status == "SUCCESS"
        assert resp.tool_called == "get_at_risk_students"
        assert any(s["student_name"] in resp.reply for s in at_risk)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Individual Student Performance & Privacy
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_individual_student_query_and_privacy():
    """Verifies specific student performance resolution and privacy protection."""
    async with AsyncSessionLocal() as db:
        t_res = await db.execute(select(TrainerProfile).where(TrainerProfile.id == 1))
        trainer = t_res.scalar_one()
        ctx = await build_trainer_context(db, trainer)

        tool_res = await tool_get_student_performance(ctx, db, student_name="Rahul Kumar")
        assert "student_name" in tool_res
        assert tool_res["student_name"] == "Rahul Kumar"
        assert "readiness_score" in tool_res
        assert "aptitude_score" in tool_res
        assert "coding_score" in tool_res
        assert "strong_areas" in tool_res
        assert "weak_areas" in tool_res

        # Privacy checks: no authentication secrets or credentials
        assert "password" not in tool_res
        assert "token" not in tool_res
        assert "phone" not in tool_res

        # Through full pipeline
        mock_provider = MockLLMProvider()
        resp = await process_trainer_query(
            query="How is Rahul Kumar performing?",
            trainer_profile=trainer,
            db=db,
            provider=mock_provider,
        )
        assert resp.status == "SUCCESS"
        assert resp.tool_called == "get_student_performance"
        assert "Rahul Kumar" in resp.reply
        assert "Readiness Score" in resp.reply


# ─────────────────────────────────────────────────────────────────────────────
# 6. Ambiguous Student Name Resolution
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ambiguous_student_name_resolution():
    """Verifies that asking for an ambiguous first name (e.g. Rahul) prompts for clarification."""
    async with AsyncSessionLocal() as db:
        t_res = await db.execute(select(TrainerProfile).where(TrainerProfile.id == 1))
        trainer = t_res.scalar_one()
        ctx = await build_trainer_context(db, trainer)

        # In Trainer 1's batches, we seeded both Rahul Kumar and Rahul Sharma
        resolution = await resolve_authorized_student(ctx, db, student_name="Rahul")
        assert resolution.get("ambiguous") is True
        assert "multiple students" in resolution.get("message", "").lower()
        assert len(resolution.get("candidates", [])) >= 2


# ─────────────────────────────────────────────────────────────────────────────
# 7. Batch Performance: Overview + Individual Student Breakdown
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_batch_performance_breakdown():
    """Verifies that 'How is my batch performing?' returns batch metrics and student breakdown."""
    async with AsyncSessionLocal() as db:
        t_res = await db.execute(select(TrainerProfile).where(TrainerProfile.id == 1))
        trainer = t_res.scalar_one()
        ctx = await build_trainer_context(db, trainer)

        tool_res = await tool_get_batch_summary(ctx, db)
        assert tool_res["total_students"] > 0
        assert "avg_readiness" in tool_res
        assert "avg_aptitude_score" in tool_res
        assert "avg_coding_score" in tool_res
        assert "students" in tool_res

        students = tool_res["students"]
        assert len(students) >= 1
        for s in students:
            assert "student_name" in s
            assert "readiness" in s
            assert "aptitude" in s
            assert "coding" in s
            assert "status" in s

        # Pipeline test
        mock_provider = MockLLMProvider()
        resp = await process_trainer_query(
            query="How is my batch performing?",
            trainer_profile=trainer,
            db=db,
            provider=mock_provider,
        )
        assert resp.status == "SUCCESS"
        assert resp.tool_called == "get_batch_summary"
        assert "Batch Overview" in resp.reply
        assert "Student Performance" in resp.reply


# ─────────────────────────────────────────────────────────────────────────────
# 8. Top Performers Query
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_top_students_ranked():
    """Verifies that 'Who are the top 5 coding performers?' ranks students correctly."""
    async with AsyncSessionLocal() as db:
        t_res = await db.execute(select(TrainerProfile).where(TrainerProfile.id == 1))
        trainer = t_res.scalar_one()
        ctx = await build_trainer_context(db, trainer)

        tool_res = await tool_get_top_students(ctx, db, metric="coding", limit=5)
        assert tool_res["ranking_metric"] == "Coding Score"
        assert len(tool_res["top_students"]) <= 5
        top = tool_res["top_students"]
        assert len(top) >= 1

        # Check ranking descending
        scores = [s["ranking_score"] for s in top]
        assert scores == sorted(scores, reverse=True)
        assert top[0]["rank"] == 1
        assert "student_name" in top[0]

        # Pipeline test
        mock_provider = MockLLMProvider()
        resp = await process_trainer_query(
            query="Who are the top 5 coding performers?",
            trainer_profile=trainer,
            db=db,
            provider=mock_provider,
        )
        assert resp.status == "SUCCESS"
        assert resp.tool_called == "get_top_students"
        assert top[0]["student_name"] in resp.reply


# ─────────────────────────────────────────────────────────────────────────────
# 9. Server-Side RBAC Enforcement: Cross-Batch Access Strictly Denied
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rbac_unauthorized_batch_denied():
    """Verifies that a trainer querying an unauthorized batch is strictly blocked server-side."""
    async with AsyncSessionLocal() as db:
        # Trainer 1 querying Batch 3 (assigned to Trainer 2)
        t_res = await db.execute(select(TrainerProfile).where(TrainerProfile.id == 1))
        trainer = t_res.scalar_one()
        ctx = await build_trainer_context(db, trainer)

        # Batch 3 belongs to Trainer 2
        b3_res = await db.execute(select(Batch.id).where(Batch.trainer_id == 2).limit(1))
        b3_id = b3_res.scalar_one_or_none()
        if b3_id:
            # 1. Weak students in unauthorized batch
            res = await tool_get_weak_students(ctx, db, batch_id=b3_id)
            assert "error" in res
            assert "Access Denied" in res["error"]

            # 2. Batch summary in unauthorized batch
            res2 = await tool_get_batch_summary(ctx, db, batch_id=b3_id)
            assert "error" in res2
            assert "Access Denied" in res2["error"]

            # 3. Placement readiness in unauthorized batch
            res3 = await tool_get_placement_readiness(ctx, db, batch_id=b3_id)
            assert "error" in res3
            assert "Access Denied" in res3["error"]
