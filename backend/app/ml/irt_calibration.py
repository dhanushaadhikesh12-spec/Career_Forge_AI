"""
Item Response Theory (IRT) empirical difficulty recalibration engine.
Uses student response history to recalibrate question difficulty parameter 'b'
using Bayesian smoothed empirical log-odds.
"""
from __future__ import annotations
import math
from typing import Dict, Any, List


def recalibrate_question_difficulty(
    prior_difficulty: float,
    attempt_count: int,
    correct_count: int,
    student_abilities: List[float] = None
) -> Dict[str, Any]:
    """
    Recalibrate item difficulty parameter b in the 1PL Rasch model:
    P(theta, b) = 1 / (1 + exp(-(theta - b)))

    Inverts the response rate using Bayesian smoothing:
    p_hat = (correct_count + 1) / (attempt_count + 2)  (Laplace smoothing)
    b_empirical = -ln(p_hat / (1 - p_hat))

    Weighted update between prior b and empirical observation:
    weight = min(0.8, attempt_count / 50.0)
    b_new = (1 - weight) * prior_b + weight * b_empirical
    """
    if attempt_count <= 0:
        return {
            "prior_difficulty": prior_difficulty,
            "calibrated_difficulty": prior_difficulty,
            "delta": 0.0,
            "confidence": "PRIOR_ONLY",
            "empirical_success_rate": 0.0,
        }

    # Laplace smoothed success probability
    p_hat = (correct_count + 1.0) / (attempt_count + 2.0)
    p_hat = min(0.98, max(0.02, p_hat))

    # Rasch empirical difficulty: b = -logit(p) = ln((1-p)/p)
    b_empirical = math.log((1.0 - p_hat) / p_hat)

    # Adjust for student cohort average ability if provided
    if student_abilities and len(student_abilities) > 0:
        avg_theta = sum(student_abilities) / len(student_abilities)
        b_empirical += avg_theta

    # Weight increases with number of attempts (up to 80% weight at 50 attempts)
    weight = min(0.85, attempt_count / 40.0)
    b_calibrated = (1.0 - weight) * prior_difficulty + weight * b_empirical

    # Bound to standard Rasch range [-3.0, +3.0]
    b_calibrated = round(min(3.0, max(-3.0, b_calibrated)), 2)

    confidence = "HIGH" if attempt_count >= 30 else "MODERATE" if attempt_count >= 10 else "PRELIMINARY"

    return {
        "prior_difficulty": round(prior_difficulty, 2),
        "calibrated_difficulty": b_calibrated,
        "delta": round(b_calibrated - prior_difficulty, 2),
        "attempt_count": attempt_count,
        "correct_count": correct_count,
        "empirical_success_rate": round((correct_count / attempt_count) * 100, 1),
        "confidence": confidence,
    }
