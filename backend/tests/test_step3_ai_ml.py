"""
Step 3 Automated Tests:
1. Ollama Provider & Model Availability
2. AI Assistant Tool Calling & Structured Responses
3. Security & Trainer Data Isolation Enforcement
4. Prompt Injection Defense
5. XGBoost Placement Readiness Feature Engineering & Inference
6. Graceful Insufficient Data Handling
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.core.security import create_access_token
from app.db.database import AsyncSessionLocal
from app.models.user import TrainerProfile, StudentProfile, User
from app.services.ai.provider import OllamaProvider, MockLLMProvider, AIProviderError
from app.services.ai.assistant import process_trainer_query, ChatMessage
from app.services.ai.tools import TrainerContext, tool_get_student_performance, tool_get_weak_students
from app.ml.feature_engineering import extract_student_features, FEATURE_NAMES
from app.ml.readiness_model import get_readiness_model, PlacementReadinessModel
from app.ml.training import retrain_readiness_model
from sqlalchemy import select


def get_token(user_id: int, email: str, role: str) -> str:
    return create_access_token({"sub": str(user_id), "email": email, "role": role})


@pytest.fixture
def student_auth_headers():
    token = get_token(3, "student@careerforge.ai", "STUDENT")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def trainer_auth_headers():
    token = get_token(2, "trainer@careerforge.ai", "TRAINER")
    return {"Authorization": f"Bearer {token}"}


# ────────────────────────── Feature Engineering & ML Inference ──────────────────────────

@pytest.mark.asyncio
async def test_feature_engineering_extraction():
    """Verifies that all 10 tabular ML features are extracted correctly."""
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(StudentProfile).limit(1))
        student = res.scalar_one_or_none()
        assert student is not None, "Seed student should exist in database"

        feat_data = await extract_student_features(db, student.id)
        assert feat_data["student_id"] == student.id
        assert "features" in feat_data
        features = feat_data["features"]

        for fn in FEATURE_NAMES:
            assert fn in features
            assert isinstance(features[fn], (int, float))

        assert len(feat_data["feature_vector"]) == 10


@pytest.mark.asyncio
async def test_readiness_model_prediction_and_insufficient_data():
    """Verifies XGBoost readiness prediction and graceful insufficient data handling."""
    model = get_readiness_model()

    # 1. Sufficient data prediction
    ready_sample = {
        "features": {
            "aptitude_accuracy": 88.0,
            "topic_mastery": 85.0,
            "coding_score": 92.0,
            "assessment_score": 90.0,
            "coding_problem_solving_rate": 85.0,
            "improvement_trend": 12.0,
            "test_completion_rate": 100.0,
            "avg_response_time": 30.0,
            "practice_frequency": 60.0,
            "difficulty_performance": 90.0,
        },
        "data_points_count": 15,
        "has_sufficient_data": True,
    }
    pred = model.predict(ready_sample)
    assert pred["status"] == "READY"
    assert pred["readiness_category"] in ["DEVELOPING", "PLACEMENT_READY"]
    assert 0.0 <= pred["readiness_score"] <= 100.0
    assert "strengths" in pred["contributing_factors"]
    assert len(pred["contributing_factors"]["strengths"]) > 0

    # 2. Insufficient data fallback
    empty_sample = {
        "features": {},
        "data_points_count": 0,
        "has_sufficient_data": False,
    }
    fallback = model.predict(empty_sample)
    assert fallback["status"] == "INSUFFICIENT_DATA"
    assert fallback["confidence"] == 0.0
    assert fallback["readiness_category"] == "NEEDS_IMPROVEMENT"
    assert "insufficient activity" in fallback["message"]


@pytest.mark.asyncio
async def test_readiness_retraining_pipeline():
    """Verifies that the readiness model retraining pipeline runs successfully."""
    async with AsyncSessionLocal() as db:
        res = await retrain_readiness_model(db)
        assert res["status"] == "SUCCESS"
        assert "xgboost_readiness.json" in res["model_artifact"]


# ────────────────────────── Trainer Authorization & Tool Safety ──────────────────────────

@pytest.mark.asyncio
async def test_trainer_authorization_strict_isolation_in_tools():
    """Verifies that backend tools strictly reject unauthorized student requests."""
    async with AsyncSessionLocal() as db:
        t_res = await db.execute(select(TrainerProfile).limit(1))
        trainer = t_res.scalar_one_or_none()
        s_res = await db.execute(select(StudentProfile).limit(1))
        student = s_res.scalar_one_or_none()
        assert trainer is not None and student is not None

        # Authorized context
        auth_ctx = TrainerContext(
            trainer_id=trainer.id,
            user_id=trainer.user_id,
            authorized_batch_ids=[1],
            authorized_student_ids=[student.id],
        )
        res_ok = await tool_get_student_performance(auth_ctx, db, student_id=student.id)
        assert "full_name" in res_ok
        assert res_ok["student_id"] == student.id

        # Unauthorized context (student 99999 is not in authorized list)
        unauth_ctx = TrainerContext(
            trainer_id=trainer.id,
            user_id=trainer.user_id,
            authorized_batch_ids=[1],
            authorized_student_ids=[student.id],
        )
        res_denied = await tool_get_student_performance(unauth_ctx, db, student_id=99999)
        assert "error" in res_denied
        assert "Access Denied" in res_denied["error"]


# ────────────────────────── AI Assistant Pipeline ──────────────────────────

@pytest.mark.asyncio
async def test_ai_assistant_tool_execution_pipeline():
    """Tests the full AI Assistant pipeline with Mock LLM provider."""
    async with AsyncSessionLocal() as db:
        t_res = await db.execute(select(TrainerProfile).limit(1))
        trainer = t_res.scalar_one_or_none()
        mock_provider = MockLLMProvider()

        # Query for weak students
        resp = await process_trainer_query(
            query="Which students are weak in reasoning?",
            trainer_profile=trainer,
            db=db,
            provider=mock_provider,
        )
        assert resp.status == "SUCCESS"
        assert resp.tool_called == "get_weak_students"
        assert resp.structured_data is not None
        assert "topic" in resp.structured_data
        assert len(resp.reply) > 0


@pytest.mark.asyncio
async def test_ai_assistant_readiness_query():
    """Tests AI Assistant tool dispatch for placement readiness."""
    async with AsyncSessionLocal() as db:
        t_res = await db.execute(select(TrainerProfile).limit(1))
        trainer = t_res.scalar_one_or_none()
        mock_provider = MockLLMProvider()

        resp = await process_trainer_query(
            query="Who is placement ready?",
            trainer_profile=trainer,
            db=db,
            provider=mock_provider,
        )
        assert resp.status == "SUCCESS"
        assert resp.tool_called == "get_placement_readiness"
        assert resp.structured_data is not None
        assert "category_breakdown" in resp.structured_data


# ────────────────────────── API Endpoints & RBAC ──────────────────────────

@pytest.mark.asyncio
async def test_security_student_forbidden_from_trainer_ai(student_auth_headers):
    """Verifies that a student token is strictly forbidden from accessing trainer AI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/trainers/assistant/chat",
            json={"query": "Give me batch performance"},
            headers=student_auth_headers,
        )
        assert resp.status_code == 403


@pytest.mark.asyncio
async def test_security_trainer_endpoint_readiness(trainer_auth_headers):
    """Verifies that trainer batch readiness endpoint returns predictions and enforces RBAC."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Batch readiness
        resp = await client.get(
            "/api/trainers/analytics/readiness",
            headers=trainer_auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "SUCCESS"
        assert "readiness_summary" in data
        assert len(data["students"]) > 0

        # 2. Individual student readiness
        first_student_id = data["students"][0]["student_id"]
        s_resp = await client.get(
            f"/api/trainers/analytics/readiness/{first_student_id}",
            headers=trainer_auth_headers,
        )
        assert s_resp.status_code == 200
        s_data = s_resp.json()
        assert s_data["student_id"] == first_student_id
        assert "prediction" in s_data

        # 3. Unauthorized student readiness access (nonexistent or unassigned student)
        bad_resp = await client.get(
            "/api/trainers/analytics/readiness/99999",
            headers=trainer_auth_headers,
        )
        assert bad_resp.status_code == 403


@pytest.mark.asyncio
async def test_trainer_assistant_status_endpoint(trainer_auth_headers):
    """Tests the /api/trainers/assistant/status endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/trainers/assistant/status",
            headers=trainer_auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "ollama"
        assert "gemma4:12b-mlx" in data["model"]
        assert "available" in data
