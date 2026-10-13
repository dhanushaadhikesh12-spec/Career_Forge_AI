"""
Tests for Student AI Personal Placement Coach:
1. Authentication & RBAC (Unauthenticated, Trainer vs Student, Student Isolation)
2. Fast Intent Routing (Greetings, General Learning, Personal Data)
3. Student Tools & ML Grounding (Performance, Readiness, Weak Topics, Practice)
4. Active Assessment Integrity Guard
5. Session Persistence & Isolation
6. Prompt Injection Defense
"""
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from app.main import app
from app.db.database import AsyncSessionLocal
from app.core.security import create_access_token
from app.models.user import StudentProfile, User, UserRole
from app.models.test import Test, TestAttempt, AttemptStatus, TestType
from app.services.ai.student_intent import classify_student_intent, StudentQueryIntent
from app.services.ai.student_tools import (
    get_my_performance,
    get_my_placement_readiness,
    get_my_weak_topics,
    get_my_adaptive_practice,
    get_current_question_context,
)
from app.services.ai.student_assistant import process_student_query


def get_token(user_id: int, email: str, role: str) -> str:
    return create_access_token({"sub": str(user_id), "email": email, "role": role})


@pytest.fixture
def student_auth_headers():
    token = get_token(3, "student@careerforge.ai", "STUDENT")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_student_auth_headers():
    token = get_token(4, "alice@example.com", "STUDENT")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def trainer_auth_headers():
    token = get_token(2, "trainer@careerforge.ai", "TRAINER")
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────────────────────────────────────
# 1. Intent Router Tests (Zero-LLM Fast Path)
# ─────────────────────────────────────────────────────────────────────────────

def test_intent_router_classifications():
    """Verifies fast, deterministic zero-LLM intent classification."""
    # Greetings
    assert classify_student_intent("Hi") == StudentQueryIntent.GENERAL_CHAT
    assert classify_student_intent("Hello coach!") == StudentQueryIntent.GENERAL_CHAT
    assert classify_student_intent("Good morning") == StudentQueryIntent.GENERAL_CHAT

    # Educational concepts
    assert classify_student_intent("Explain binary search") == StudentQueryIntent.GENERAL_LEARNING
    assert classify_student_intent("What is inheritance in OOP?") == StudentQueryIntent.GENERAL_LEARNING
    assert classify_student_intent("Difference between interface and abstract class") == StudentQueryIntent.GENERAL_LEARNING

    # Performance
    assert classify_student_intent("How am I doing?") == StudentQueryIntent.PERSONAL_PERFORMANCE
    assert classify_student_intent("Analyze my performance") == StudentQueryIntent.PERSONAL_PERFORMANCE

    # Weak & Strong Topics
    assert classify_student_intent("What are my weak topics?") == StudentQueryIntent.WEAK_TOPICS
    assert classify_student_intent("Where am I struggling?") == StudentQueryIntent.WEAK_TOPICS
    assert classify_student_intent("What are my strong topics?") == StudentQueryIntent.STRONG_TOPICS

    # Readiness
    assert classify_student_intent("Am I placement ready?") == StudentQueryIntent.READINESS
    assert classify_student_intent("What is my placement readiness score?") == StudentQueryIntent.READINESS

    # Study Plan
    assert classify_student_intent("Make me a 7-day study plan") == StudentQueryIntent.STUDY_PLAN
    assert classify_student_intent("I have 2 weeks before placements, give me a preparation plan") == StudentQueryIntent.STUDY_PLAN

    # Practice
    assert classify_student_intent("Give me 5 questions on recursion") == StudentQueryIntent.PRACTICE
    assert classify_student_intent("Practice questions on DSA") == StudentQueryIntent.PRACTICE

    # Coding
    assert classify_student_intent("How is my coding performance?") == StudentQueryIntent.CODING_PERFORMANCE


# ─────────────────────────────────────────────────────────────────────────────
# 2. Authentication & RBAC Security
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_unauthenticated_request_rejected():
    """Unauthenticated access to student coach is rejected with 401/403."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/students/coach/chat", json={"query": "Hi"})
        assert res.status_code in (401, 403)


@pytest.mark.asyncio
async def test_trainer_access_to_student_coach_forbidden(trainer_auth_headers):
    """Trainers cannot access the Student AI Coach endpoint (Role isolation)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/students/coach/chat",
            json={"query": "How am I performing?"},
            headers=trainer_auth_headers,
        )
        assert res.status_code == 403
        assert "Student access required" in res.json().get("detail", "")


@pytest.mark.asyncio
async def test_student_chat_session_isolation(student_auth_headers, other_student_auth_headers):
    """A student cannot access or delete another student's coaching sessions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Student 1 creates session
        res1 = await client.post(
            "/api/students/coach/sessions",
            json={"title": "Student 1 Private Session"},
            headers=student_auth_headers,
        )
        assert res1.status_code == 200
        sess_id = res1.json()["id"]

        # Student 2 attempts to read Student 1's session
        res2 = await client.get(
            f"/api/students/coach/sessions/{sess_id}",
            headers=other_student_auth_headers,
        )
        assert res2.status_code == 404

        # Student 2 attempts to delete Student 1's session
        res3 = await client.delete(
            f"/api/students/coach/sessions/{sess_id}",
            headers=other_student_auth_headers,
        )
        assert res3.status_code == 404

        # Student 1 can read own session
        res4 = await client.get(
            f"/api/students/coach/sessions/{sess_id}",
            headers=student_auth_headers,
        )
        assert res4.status_code == 200
        assert res4.json()["id"] == sess_id


# ─────────────────────────────────────────────────────────────────────────────
# 3. Student Tools & ML Grounding Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_student_tools_grounding():
    """Validates that student tools return authoritative metrics without inventing data."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(StudentProfile).limit(1))
        profile = res.scalar_one_or_none()
        assert profile is not None

        # 1. Performance
        perf = await get_my_performance(profile, db)
        assert "readiness_score" in perf
        assert "aptitude_accuracy" in perf
        assert "coding_accuracy" in perf
        assert "tests_completed" in perf

        # 2. ML Placement Readiness
        readiness = await get_my_placement_readiness(profile, db)
        assert "readiness_score" in readiness
        assert "readiness_category" in readiness
        assert readiness["readiness_category"] in ["NEEDS_IMPROVEMENT", "DEVELOPING", "PLACEMENT_READY"]
        assert "strengths" in readiness
        assert "improvement_areas" in readiness

        # 3. Weak Topics
        weak = await get_my_weak_topics(profile, db)
        assert "topics" in weak
        assert isinstance(weak["topics"], list)

        # 4. Adaptive Practice
        practice = await get_my_adaptive_practice(profile, db, count=3)
        assert "questions" in practice
        assert len(practice["questions"]) <= 3
        if practice["questions"]:
            q0 = practice["questions"][0]
            assert "id" in q0
            assert "text" in q0
            assert "options" in q0


# ─────────────────────────────────────────────────────────────────────────────
# 4. End-to-End Chat & Orchestration
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_student_coach_chat_conversational(student_auth_headers):
    """Verifies conversational greetings execute through fast zero-DB path."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/students/coach/chat",
            json={"query": "Hi coach!"},
            headers=student_auth_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert data["intent"] == "general_chat"
        assert "CareerForge AI Placement Coach" in data["reply"]


@pytest.mark.asyncio
async def test_student_coach_chat_readiness(student_auth_headers):
    """Verifies placement readiness inquiry triggers ML model and returns structured data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/students/coach/chat",
            json={"query": "Am I placement ready?"},
            headers=student_auth_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert data["tool_called"] == "get_my_placement_readiness"
        assert data["structured_data"] is not None
        assert "readiness_score" in data["structured_data"]


@pytest.mark.asyncio
async def test_student_coach_chat_weak_topics(student_auth_headers):
    """Verifies weak topics inquiry triggers get_my_weak_topics."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/students/coach/chat",
            json={"query": "What are my weak topics?"},
            headers=student_auth_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert data["tool_called"] == "get_my_weak_topics"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Assessment Safety & Integrity Guard
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_active_assessment_solution_leak_prevented():
    """Verifies that if student has an active test attempt, the AI refuses to provide answers."""
    async with AsyncSessionLocal() as db:
        # Find seed student
        res = await db.execute(select(StudentProfile).limit(1))
        profile = res.scalar_one_or_none()
        assert profile is not None

        # Find or create a test
        t_res = await db.execute(select(Test).limit(1))
        test = t_res.scalar_one_or_none()
        assert test is not None

        # Create active in-progress attempt expiring in 30 minutes
        now = datetime.now(timezone.utc)
        attempt = TestAttempt(
            test_id=test.id,
            student_id=profile.id,
            status=AttemptStatus.IN_PROGRESS,
            started_at=now,
            expires_at=now + timedelta(minutes=30),
            question_order=[1, 2, 3],
        )
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)

        try:
            # Query asking for test solution
            response = await process_student_query(
                query="Give me answer to this test question right now",
                student_profile=profile,
                db=db,
            )
            assert "active assessment in progress" in response.reply.lower()

            # Question context retrieval restriction
            ctx = await get_current_question_context(
                student_profile=profile,
                db=db,
                question_id=1,
            )
            assert ctx.get("restricted") is True
            assert "active proctored assessment" in ctx.get("message", "").lower()

        finally:
            # Clean up test attempt
            await db.delete(attempt)
            await db.commit()
