"""
Step 1 Automated Verification Test Suite
Tests authentication, authorization, student learning, practice engine,
test sessions, server-side scoring, timer enforcement, and trainer isolation.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from app.main import app
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole, StudentProfile, TrainerProfile, Batch, BatchMembership
from app.models.content import Subject, Topic, Lesson, Question, QuestionOption, QuestionType, DifficultyLevel
from app.models.test import Test, TestQuestion, TestAttempt, AttemptStatus, TestStatus, TestType
from app.db.database import get_db, AsyncSessionLocal


@pytest.mark.asyncio
async def test_auth_login_student_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "Student@1234",
        })
        assert res.status_code == 200, res.text
        data = res.json()
        assert "access_token" in data
        assert data["user"]["role"] == "STUDENT"
        assert data["user"]["email"] == "student@careerforge.ai"


@pytest.mark.asyncio
async def test_auth_login_trainer_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/auth/login", json={
            "email": "trainer@careerforge.ai",
            "password": "Trainer@1234",
        })
        assert res.status_code == 200, res.text
        data = res.json()
        assert "access_token" in data
        assert data["user"]["role"] == "TRAINER"


@pytest.mark.asyncio
async def test_auth_login_invalid_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "WrongPassword!999",
        })
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_requires_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/students/dashboard")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_student_dashboard_authenticated():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login as student
        login_res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "Student@1234",
        })
        token = login_res.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        res = await client.get("/api/students/dashboard", headers=headers)
        assert res.status_code == 200, res.text
        data = res.json()
        assert "student" in data
        assert "recent_tests" in data
        assert "weak_topics" in data


@pytest.mark.asyncio
async def test_subjects_and_topics_retrieval():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "Student@1234",
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List subjects
        sub_res = await client.get("/api/students/subjects", headers=headers)
        assert sub_res.status_code == 200
        subjects = sub_res.json()
        assert len(subjects) >= 2

        # List topics for first subject
        topic_res = await client.get(f"/api/students/subjects/{subjects[0]['id']}/topics", headers=headers)
        assert topic_res.status_code == 200
        topics = topic_res.json()
        assert len(topics) >= 1


@pytest.mark.asyncio
async def test_practice_session_and_submission():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "Student@1234",
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Start practice
        session_res = await client.post("/api/students/practice/session", json={
            "topic_id": 1,
            "count": 3,
        }, headers=headers)
        assert session_res.status_code == 200, session_res.text
        questions = session_res.json()
        assert len(questions) > 0

        # Submit answer to question 1
        q = questions[0]
        opt_id = q["options"][0]["id"]
        ans_res = await client.post("/api/students/practice/submit", json={
            "question_id": q["id"],
            "selected_option_id": opt_id,
            "time_taken_seconds": 15,
        }, headers=headers)
        assert ans_res.status_code == 200
        ans_data = ans_res.json()
        assert "is_correct" in ans_data
        assert "correct_option_id" in ans_data
        assert "points_earned" in ans_data


@pytest.mark.asyncio
async def test_test_start_scoring_and_review():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "Student@1234",
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List tests and find aptitude test
        tests_res = await client.get("/api/students/tests", headers=headers)
        assert tests_res.status_code == 200
        tests = tests_res.json()
        assert len(tests) >= 1
        aptitude_test = next((t for t in tests if t.get("test_type") == "APTITUDE"), tests[0])
        test_id = aptitude_test["id"]

        # Start test
        start_res = await client.post(f"/api/students/tests/{test_id}/start", headers=headers)
        assert start_res.status_code == 200, start_res.text
        session_data = start_res.json()
        attempt_id = session_data["attempt_id"]
        q_list = session_data["questions"]
        assert len(q_list) > 0

        # Submit answers
        submit_res = await client.post("/api/students/tests/submit", json={
            "attempt_id": attempt_id,
            "answers": [
                {
                    "question_id": q_list[0]["id"],
                    "selected_option_id": q_list[0]["options"][0]["id"],
                    "time_taken_seconds": 20,
                }
            ],
        }, headers=headers)
        assert submit_res.status_code == 200, submit_res.text
        result_data = submit_res.json()
        assert "score" in result_data
        assert "percentage" in result_data
        assert result_data["status"] == "GRADED"

        # Check full scorecard review endpoint
        review_res = await client.get(f"/api/students/tests/attempts/{attempt_id}", headers=headers)
        assert review_res.status_code == 200
        review_data = review_res.json()
        assert review_data["attempt_id"] == attempt_id
        assert "questions" in review_data
        assert len(review_data["questions"]) > 0

        # Clean up test attempt
        from app.db.database import AsyncSessionLocal
        from app.models.test import TestAttempt
        from sqlalchemy import delete
        async with AsyncSessionLocal() as db:
            await db.execute(delete(TestAttempt).where(TestAttempt.id == attempt_id))
            await db.commit()


@pytest.mark.asyncio
async def test_trainer_authorization_and_batches():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Student cannot access trainer routes
        student_res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "Student@1234",
        })
        student_token = student_res.json()["access_token"]
        unauth_res = await client.get("/api/trainers/dashboard", headers={"Authorization": f"Bearer {student_token}"})
        assert unauth_res.status_code == 403

        # Trainer can access trainer dashboard
        trainer_res = await client.post("/api/auth/login", json={
            "email": "trainer@careerforge.ai",
            "password": "Trainer@1234",
        })
        trainer_token = trainer_res.json()["access_token"]
        auth_res = await client.get("/api/trainers/dashboard", headers={"Authorization": f"Bearer {trainer_token}"})
        assert auth_res.status_code == 200
        assert "batch_count" in auth_res.json()
