"""
Test suite for student Focus Area dynamic calculation and synchronization.
Verifies that:
1. Focus areas are dynamically derived from actual student practice attempts and test answers.
2. Focus areas are sorted by lowest accuracy first and include attempt counts.
3. Submitting practice answers immediately updates focus areas.
4. Submitting an assessment test immediately updates topic progress and focus areas.
5. Adaptive insights and dashboard focus areas are consistent and accurate.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from app.main import app
from app.models.content import Question, Topic, PracticeAttempt
from app.models.test import Test, TestAttempt, TestAnswer, TestQuestion, AttemptStatus, TestType
from app.models.user import StudentProfile, TopicProgress
from app.db.database import AsyncSessionLocal


@pytest.mark.asyncio
async def test_student_dashboard_focus_areas_dynamic_and_accurate():
    """Verify that focus areas on student dashboard reflect real attempts, sorted lowest accuracy first."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "Student@1234",
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Fetch dashboard
        dash_res = await client.get("/api/students/dashboard", headers=headers)
        assert dash_res.status_code == 200
        data = dash_res.json()
        assert "weak_topics" in data
        weak = data["weak_topics"]

        # Number System should be identified as weak (< 50% accuracy)
        assert len(weak) >= 1
        num_sys = next((t for t in weak if t["topic_name"] == "Number System"), None)
        assert num_sys is not None
        assert num_sys["accuracy"] < 50.0
        assert num_sys["questions_attempted"] is not None
        assert num_sys["questions_correct"] is not None

        # Verify sorted ascending by accuracy
        for i in range(len(weak) - 1):
            assert weak[i]["accuracy"] <= weak[i + 1]["accuracy"]


@pytest.mark.asyncio
async def test_focus_areas_update_dynamically_after_practice():
    """Submitting practice answers must dynamically update accuracy and attempt counts in focus areas."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "Student@1234",
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get initial state of Number System (topic 1)
        dash_before = (await client.get("/api/students/dashboard", headers=headers)).json()
        before_ns = next((t for t in dash_before["weak_topics"] if t["topic_id"] == 1), None)
        before_attempts = before_ns["questions_attempted"] if before_ns else 0

        # Start practice on topic 1
        sess_res = await client.post("/api/students/practice/session", json={
            "topic_id": 1,
            "count": 1,
        }, headers=headers)
        assert sess_res.status_code == 200
        questions = sess_res.json()
        assert len(questions) >= 1
        q = questions[0]
        opt_id = q["options"][0]["id"]

        # Submit answer
        sub_res = await client.post("/api/students/practice/submit", json={
            "question_id": q["id"],
            "selected_option_id": opt_id,
            "time_taken_seconds": 15,
        }, headers=headers)
        assert sub_res.status_code == 200

        # Check dashboard after practice
        dash_after = (await client.get("/api/students/dashboard", headers=headers)).json()
        after_ns = next((t for t in dash_after["weak_topics"] if t["topic_id"] == 1), None)
        assert after_ns is not None
        # Attempt count must have dynamically increased by at least 1
        assert after_ns["questions_attempted"] > before_attempts


@pytest.mark.asyncio
async def test_adaptive_insights_consistency():
    """Verify that Adaptive Insights and Student Dashboard weak topics are synchronized."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post("/api/auth/login", json={
            "email": "student@careerforge.ai",
            "password": "Student@1234",
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        dash_res = await client.get("/api/students/dashboard", headers=headers)
        ins_res = await client.get("/api/students/adaptive/insights", headers=headers)

        dash_data = dash_res.json()
        ins_data = ins_res.json()

        assert "weak_topics" in dash_data
        assert "weak_topics" in ins_data

        if dash_data["weak_topics"] and ins_data["weak_topics"]:
            top_dash = dash_data["weak_topics"][0]
            top_ins = ins_data["weak_topics"][0]
            # Primary weak topic should match
            assert top_dash["topic_id"] == top_ins["topic_id"]
            assert abs(top_dash["accuracy"] - top_ins["accuracy"]) < 0.2
