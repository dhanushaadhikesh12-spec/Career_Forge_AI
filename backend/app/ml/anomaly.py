"""
Isolation Forest anomaly detection engine for identifying suspicious assessment behavior.
Detects statistical outliers across submission velocity, timing patterns, and proctoring events.
"""
from __future__ import annotations
import logging
from typing import List, Dict, Any
import numpy as np
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)


def detect_assessment_anomalies(attempt_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates assessment attempts using Isolation Forest on:
    - duration_seconds (speed of completion)
    - score_percentage
    - violation_count (tab switches, blurs, etc.)
    - submission_count (rapid submit attempts)
    - avg_time_per_question

    Returns:
    {
        "status": "SUCCESS" | "INSUFFICIENT_DATA",
        "anomalies": [...],
        "total_evaluated": int
    }
    """
    n_attempts = len(attempt_data)
    # IsolationForest requires statistically meaningful sample size (min 5 attempts)
    if n_attempts < 4:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": f"Isolation Forest anomaly detection requires at least 4 test attempts (current: {n_attempts}).",
            "min_required": 4,
            "current_count": n_attempts,
            "anomalies": [],
            "total_evaluated": n_attempts,
        }

    features = []
    for a in attempt_data:
        duration = float(a.get("duration_seconds") or 300.0)
        score = float(a.get("percentage") or 0.0)
        violations = float(a.get("violation_count") or 0.0)
        subs = float(a.get("submission_count") or 1.0)
        avg_time = float(a.get("avg_time_per_question") or 60.0)
        features.append([duration, score, violations, subs, avg_time])

    X = np.array(features, dtype=float)

    # Contamination set to 15% (estimated expected outlier rate)
    iso_forest = IsolationForest(
        contamination=min(0.25, max(0.05, 1.0 / n_attempts)),
        random_state=42,
        n_estimators=50
    )

    preds = iso_forest.fit_predict(X)  # -1 = anomaly, 1 = normal
    scores = iso_forest.decision_function(X)  # Lower is more anomalous

    anomalies = []
    for i, a in enumerate(attempt_data):
        is_anomaly = preds[i] == -1
        anomaly_score = round(float(scores[i]), 3)

        # Highlight behavioral anomaly signals
        signals = []
        duration = X[i][0]
        score = X[i][1]
        violations = X[i][2]
        subs = X[i][3]

        if duration < 120 and score > 80:
            signals.append("Abnormally rapid completion (< 2 mins) with high score")
        if violations >= 5:
            signals.append(f"Elevated proctoring violations ({int(violations)} events)")
        if subs > 10:
            signals.append("High submission velocity / rapid automated retries")
        if duration > 3600:
            signals.append("Excessive session duration outlier")

        if is_anomaly or len(signals) > 0:
            anomalies.append({
                "attempt_id": a.get("attempt_id"),
                "student_id": a.get("student_id"),
                "student_name": a.get("student_name", "Student"),
                "test_id": a.get("test_id"),
                "test_title": a.get("test_title", "Assessment"),
                "duration_seconds": int(duration),
                "score_percentage": round(score, 1),
                "violation_count": int(violations),
                "anomaly_score": anomaly_score,
                "is_outlier": is_anomaly,
                "risk_level": "HIGH" if violations >= 5 or (duration < 120 and score > 80) else "MEDIUM",
                "detected_signals": signals if signals else ["Multivariate behavioral outlier detected by Isolation Forest"],
            })

    # Sort most anomalous first
    anomalies.sort(key=lambda x: x["anomaly_score"])

    return {
        "status": "SUCCESS",
        "anomalies": anomalies,
        "total_evaluated": n_attempts,
        "anomaly_count": len(anomalies),
    }
