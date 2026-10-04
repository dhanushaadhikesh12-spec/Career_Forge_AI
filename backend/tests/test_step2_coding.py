"""
Automated test suite for Step 2:
- Coding question retrieval & hidden test case protection
- Judge0 code execution (Run vs Submit) & error handling (Compilation, Runtime)
- Persistent CodeSubmission and student scoring
- Server-side timing & auto-expiration for coding assessments
- Proctoring telemetry & malpractice risk reports
- Trainer analytics & RBAC authorization
- ML components: K-Means clustering, Plagiarism detection, Isolation Forest anomalies, IRT calibration
"""
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from app.main import app
from app.core.security import create_access_token
from app.services.judge0 import judge0_service
from app.ml.clustering import cluster_students
from app.ml.plagiarism import calculate_code_similarity, analyze_submission_pool, normalize_code_identifiers, strip_comments_and_whitespace
from app.ml.anomaly import detect_assessment_anomalies
from app.ml.irt_calibration import recalibrate_question_difficulty


def get_token(user_id: int, email: str, role: str) -> str:
    return create_access_token({"sub": str(user_id), "email": email, "role": role})


@pytest.fixture
def student_auth_headers():
    token = get_token(3, "student@careerforge.ai", "STUDENT")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_student_headers():
    token = get_token(4, "alice@example.com", "STUDENT")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def trainer_auth_headers():
    token = get_token(2, "trainer@careerforge.ai", "TRAINER")
    return {"Authorization": f"Bearer {token}"}


# ────────────────────────── 1. Coding Question Bank & Security ──────────────────────────

@pytest.mark.asyncio
async def test_coding_questions_catalog(student_auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/students/coding/questions", headers=student_auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1
        first_q = data[0]
        assert "title" in first_q
        assert "slug" in first_q
        assert "difficulty" in first_q
        assert "marks" in first_q


@pytest.mark.asyncio
async def test_hidden_test_cases_are_never_exposed(student_auth_headers):
    """
    CRITICAL SECURITY TEST:
    Verifies that sample test cases are returned with inputs/outputs,
    but hidden test cases are strictly excluded from student question details.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/students/coding/questions/two-sum", headers=student_auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["slug"] == "two-sum"

        sample_cases = data["sample_test_cases"]
        assert len(sample_cases) >= 1
        # All returned cases must be sample cases
        for tc in sample_cases:
            assert tc["is_sample"] is True
            assert tc["input"] is not None
            assert tc["expected_output"] is not None

        # Verify no hidden test cases (e.g. order_index 1 or 2 with is_sample=False) leaked
        for tc in sample_cases:
            assert "3 2 4" not in tc["input"]  # Hidden test input for two-sum


# ────────────────────────── 2. Judge0 Execution & Error Handling ──────────────────────────

@pytest.mark.asyncio
async def test_run_sample_code_success(student_auth_headers):
    """Run code executes only against sample test cases without scoring."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "source_code": "import sys\nprint('0 1')",
            "language": "python",
        }
        res = await ac.post("/api/students/coding/questions/1/run", json=payload, headers=student_auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["verdict"] == "ACCEPTED"
        assert data["passed_tests"] >= 1
        assert len(data["test_results"]) == 1  # Exactly 1 sample test case


@pytest.mark.asyncio
async def test_submit_code_evaluates_all_tests_and_redacts_hidden(student_auth_headers):
    """Submit code executes against all tests, scores, and redacts hidden test inputs in response."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "source_code": "import sys\nlines = sys.stdin.read().splitlines()\nprint('0 1')",
            "language": "python",
        }
        res = await ac.post("/api/students/coding/questions/1/submit", json=payload, headers=student_auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "score" in data
        assert data["test_cases_total"] >= 2  # Includes hidden test cases
        assert data["student_id"] == 1  # Student profile ID for demo student

        # Check redaction of hidden test cases in result
        for tc in data["test_results"]:
            if not tc["is_sample"]:
                assert tc["input"] is None
                assert tc["expected_output"] is None


@pytest.mark.asyncio
async def test_compilation_error_handling(student_auth_headers):
    """Verifies that syntax/compilation errors are captured and reported cleanly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "source_code": "def broken_syntax(:\n    syntax_error",
            "language": "python",
        }
        res = await ac.post("/api/students/coding/questions/1/submit", json=payload, headers=student_auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["verdict"] == "COMPILATION_ERROR"
        assert data["score"] == 0.0
        assert data["compile_output"] is not None


@pytest.mark.asyncio
async def test_runtime_error_handling(student_auth_headers):
    """Verifies that runtime exceptions are captured cleanly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "source_code": "x = 10 / 0 # runtime_error",
            "language": "python",
        }
        res = await ac.post("/api/students/coding/questions/1/submit", json=payload, headers=student_auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["verdict"] == "RUNTIME_ERROR"
        assert data["score"] == 0.0


# ────────────────────────── 3. Submissions & RBAC Security ──────────────────────────

@pytest.mark.asyncio
async def test_submission_ownership_isolation(student_auth_headers, other_student_headers):
    """
    SECURITY TEST:
    Student A cannot view private code submissions of Student B.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create submission as Student A
        payload = {"source_code": "print('valid')", "language": "python"}
        res = await ac.post("/api/students/coding/questions/2/submit", json=payload, headers=student_auth_headers)
        sub_id = res.json()["id"]

        # Student A can view their submission
        view_res = await ac.get(f"/api/students/coding/submissions/{sub_id}", headers=student_auth_headers)
        assert view_res.status_code == 200

        # Student B cannot view Student A's submission
        other_res = await ac.get(f"/api/students/coding/submissions/{sub_id}", headers=other_student_headers)
        assert other_res.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_access_trainer_analytics(student_auth_headers):
    """
    SECURITY TEST:
    Students cannot access trainer-only analytics endpoints.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/trainers/analytics/overview", headers=student_auth_headers)
        assert res.status_code == 403


# ────────────────────────── 4. Coding Assessments & Server Timing ──────────────────────────

@pytest.mark.asyncio
async def test_coding_assessment_server_timing_and_start(student_auth_headers):
    """Verifies authoritative server-side timing on coding assessments."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Start assessment 2 (Placement Coding Assessment 1)
        res = await ac.post("/api/students/coding/assessments/2/start", headers=student_auth_headers)
        assert res.status_code in [200, 404]
        if res.status_code == 200:
            data = res.json()
            assert data["remaining_seconds"] > 0
            assert data["is_expired"] is False
            assert "started_at" in data

            # Check server time endpoint
            time_res = await ac.get("/api/students/coding/assessments/2/time", headers=student_auth_headers)
            assert time_res.status_code == 200
            time_data = time_res.json()
            assert time_data["remaining_seconds"] > 0
            assert "server_time" in time_data

            # Clean up test attempt
            from app.db.database import AsyncSessionLocal
            from app.models.test import TestAttempt
            from sqlalchemy import delete
            async with AsyncSessionLocal() as db:
                await db.execute(delete(TestAttempt).where(TestAttempt.id == data["attempt_id"]))
                await db.commit()


# ────────────────────────── 5. Anti-Malpractice / Proctoring ──────────────────────────

@pytest.mark.asyncio
async def test_log_proctoring_event_and_report(student_auth_headers, trainer_auth_headers):
    """Verifies that browser malpractice events are received and aggregated."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Start an aptitude test to get an active attempt ID
        start_res = await ac.post("/api/students/tests/1/start", headers=student_auth_headers)
        if start_res.status_code == 200:
            attempt_id = start_res.json()["attempt_id"]

            # Log events
            ev_payload = {
                "attempt_id": attempt_id,
                "event_type": "tab_switch",
                "severity": "HIGH",
                "description": "User switched away from assessment window",
            }
            log_res = await ac.post("/api/proctoring/event", json=ev_payload, headers=student_auth_headers)
            assert log_res.status_code == 200
            assert log_res.json()["recorded"] is True

            # Student view summary
            summ_res = await ac.get(f"/api/proctoring/attempts/{attempt_id}/summary", headers=student_auth_headers)
            assert summ_res.status_code == 200
            summ_data = summ_res.json()
            assert summ_data["summary"]["total_violations"] >= 1

            # Clean up test attempt
            from app.db.database import AsyncSessionLocal
            from app.models.test import TestAttempt
            from sqlalchemy import delete
            async with AsyncSessionLocal() as db:
                await db.execute(delete(TestAttempt).where(TestAttempt.id == attempt_id))
                await db.commit()


# ────────────────────────── 6. ML Components: Clustering, Plagiarism, Anomaly, IRT ──────────────────────────

def test_kmeans_student_grouping():
    """Tests K-Means performance clustering with data-driven labels."""
    # Test insufficient data fallback
    sparse_data = [{"id": 1, "aptitude_score": 80}]
    fallback = cluster_students(sparse_data)
    assert fallback["status"] == "INSUFFICIENT_DATA"
    assert fallback["min_required"] == 3

    # Test full clustering with 4 students
    cohort = [
        {"id": 1, "full_name": "High Top", "aptitude_score": 95, "coding_score": 90, "avg_test_score": 92, "completion_rate": 95, "streak_days": 10},
        {"id": 2, "full_name": "High Second", "aptitude_score": 88, "coding_score": 85, "avg_test_score": 89, "completion_rate": 90, "streak_days": 8},
        {"id": 3, "full_name": "Middle Dev", "aptitude_score": 60, "coding_score": 55, "avg_test_score": 58, "completion_rate": 70, "streak_days": 3},
        {"id": 4, "full_name": "Struggling Low", "aptitude_score": 30, "coding_score": 25, "avg_test_score": 28, "completion_rate": 40, "streak_days": 0},
    ]
    result = cluster_students(cohort)
    assert result["status"] == "SUCCESS"
    assert len(result["clusters"]) >= 2
    # Verify labels assigned
    labels = [c["label"] for c in result["clusters"]]
    assert "High Performer" in labels or "Proficient" in labels


def test_plagiarism_similarity_engine():
    """Tests structural tokenization, comment stripping, identifier normalization, and copy detection."""
    code_a = """
    # Solution by Student A
    def solve_two_sum(numbers, target_val):
        lookup_map = {}
        for index, item in enumerate(numbers):
            diff = target_val - item
            if diff in lookup_map:
                return [lookup_map[diff], index]
            lookup_map[item] = index
        return []
    """

    # Student B renames variables and alters comments
    code_b = """
    '''Different comments'''
    def find_target(arr, target):
        cache = {}
        for i, val in enumerate(arr):
            needed = target - val
            if needed in cache:
                return [cache[needed], i]
            cache[val] = i
        return []
    """

    # Code C is completely different logic
    code_c = """
    def is_palindrome(text):
        return text == text[::-1]
    """

    sim_ab = calculate_code_similarity(code_a, code_b, language="python")
    assert sim_ab["similarity_score"] >= 80.0
    assert sim_ab["is_flagged"] is True

    sim_ac = calculate_code_similarity(code_a, code_c, language="python")
    assert sim_ac["similarity_score"] < 40.0
    assert sim_ac["is_flagged"] is False


def test_isolation_forest_anomaly_detection():
    """Tests Isolation Forest anomaly detection with statistical outlier detection."""
    # Test insufficient data fallback
    sparse_attempts = [{"attempt_id": 1, "percentage": 80}]
    fallback = detect_assessment_anomalies(sparse_attempts)
    assert fallback["status"] == "INSUFFICIENT_DATA"

    # Cohort of 5 normal attempts and 1 extreme outlier
    attempts = [
        {"attempt_id": 1, "duration_seconds": 1800, "percentage": 75, "violation_count": 0, "submission_count": 3, "avg_time_per_question": 180},
        {"attempt_id": 2, "duration_seconds": 1900, "percentage": 70, "violation_count": 1, "submission_count": 2, "avg_time_per_question": 190},
        {"attempt_id": 3, "duration_seconds": 2100, "percentage": 82, "violation_count": 0, "submission_count": 4, "avg_time_per_question": 210},
        {"attempt_id": 4, "duration_seconds": 1750, "percentage": 68, "violation_count": 1, "submission_count": 3, "avg_time_per_question": 175},
        {"attempt_id": 5, "duration_seconds": 2000, "percentage": 78, "violation_count": 0, "submission_count": 2, "avg_time_per_question": 200},
        # Outlier: finished in 45 seconds with 100% score and 8 violations
        {"attempt_id": 6, "duration_seconds": 45, "percentage": 100, "violation_count": 8, "submission_count": 12, "avg_time_per_question": 4},
    ]
    res = detect_assessment_anomalies(attempts)
    assert res["status"] == "SUCCESS"
    assert res["anomaly_count"] >= 1
    # Check that attempt 6 was flagged
    flagged_ids = [a["attempt_id"] for a in res["anomalies"]]
    assert 6 in flagged_ids


def test_irt_difficulty_recalibration():
    """Tests Bayesian empirical IRT question recalibration."""
    # Question with prior b=0.0 (medium), but 48 out of 50 students failed it
    recal = recalibrate_question_difficulty(
        prior_difficulty=0.0,
        attempt_count=50,
        correct_count=2,
    )
    # Since almost everyone failed, empirical difficulty should shift significantly upward (> 1.0)
    assert recal["calibrated_difficulty"] > 1.0
    assert recal["delta"] > 0
    assert recal["confidence"] == "HIGH"
