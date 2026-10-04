"""
Proctoring and Anti-Malpractice system:
Captures browser telemetry (tab switches, blur, copy/paste, fullscreen exit)
and computes authoritative server-side malpractice risk reports.
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.api.deps import get_student_profile, get_trainer_profile
from app.models.user import StudentProfile, TrainerProfile
from app.models.test import TestAttempt, ProctoringEvent, AttemptStatus, Test
from app.schemas.test import ProctoringEventCreate, ProctoringEventOut
import logging

router = APIRouter(prefix="/proctoring", tags=["Proctoring"])
logger = logging.getLogger(__name__)


def now_utc():
    return datetime.now(timezone.utc)


def calculate_malpractice_risk(events: List[ProctoringEvent]) -> Dict[str, Any]:
    """
    Evaluates malpractice events and computes an objective risk assessment.
    Risk thresholds:
    - HIGH: >= 5 window/tab violations, or fullscreen exit with multiple clipboard events.
    - MEDIUM: 2-4 window/tab violations, or 1 fullscreen exit.
    - LOW: <= 1 minor event.
    """
    event_counts = {
        "tab_switch": 0,
        "window_blur": 0,
        "fullscreen_exit": 0,
        "clipboard_copy": 0,
        "clipboard_paste": 0,
        "other": 0,
    }

    for ev in events:
        etype = ev.event_type.lower()
        if "tab" in etype or "visibility" in etype:
            event_counts["tab_switch"] += 1
        elif "blur" in etype or "focus" in etype:
            event_counts["window_blur"] += 1
        elif "fullscreen" in etype:
            event_counts["fullscreen_exit"] += 1
        elif "copy" in etype:
            event_counts["clipboard_copy"] += 1
        elif "paste" in etype:
            event_counts["clipboard_paste"] += 1
        else:
            event_counts["other"] += 1

    total_violations = len(events)
    weighted_score = (
        event_counts["tab_switch"] * 2.0 +
        event_counts["window_blur"] * 1.5 +
        event_counts["fullscreen_exit"] * 4.0 +
        event_counts["clipboard_copy"] * 2.5 +
        event_counts["clipboard_paste"] * 3.0
    )

    if weighted_score >= 10.0 or total_violations >= 6 or event_counts["fullscreen_exit"] >= 2:
        risk_level = "HIGH"
    elif weighted_score >= 4.0 or total_violations >= 2 or event_counts["fullscreen_exit"] >= 1:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "total_violations": total_violations,
        "risk_level": risk_level,
        "weighted_severity_score": round(weighted_score, 1),
        "breakdown": event_counts,
    }


@router.post("/event")
async def log_proctoring_event(
    payload: ProctoringEventCreate,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Records an anti-malpractice event from the browser during a test.
    Validates that the attempt belongs to this student and is active.
    """
    result = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.id == payload.attempt_id)
        .where(TestAttempt.student_id == profile.id)
        .where(TestAttempt.status == AttemptStatus.IN_PROGRESS)
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Active test attempt not found or unauthorized")

    event = ProctoringEvent(
        attempt_id=payload.attempt_id,
        event_type=payload.event_type,
        severity=payload.severity or "LOW",
        description=payload.description,
        event_metadata=payload.event_metadata,
        occurred_at=now_utc(),
    )
    db.add(event)
    await db.commit()

    logger.warning(
        f"Proctoring violation: student={profile.id} attempt={payload.attempt_id} "
        f"type={payload.event_type} severity={payload.severity}"
    )
    return {"recorded": True}


@router.get("/attempts/{attempt_id}/summary")
async def get_attempt_malpractice_summary(
    attempt_id: int,
    profile: StudentProfile = Depends(get_student_profile),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns proctoring summary for the student's own attempt.
    """
    res = await db.execute(
        select(TestAttempt)
        .where(TestAttempt.id == attempt_id)
        .where(TestAttempt.student_id == profile.id)
        .options(selectinload(TestAttempt.proctoring_events))
    )
    attempt = res.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found or unauthorized")

    summary = calculate_malpractice_risk(attempt.proctoring_events)
    return {
        "attempt_id": attempt.id,
        "test_id": attempt.test_id,
        "summary": summary,
        "events": [
            {
                "id": ev.id,
                "event_type": ev.event_type,
                "severity": ev.severity,
                "description": ev.description,
                "occurred_at": ev.occurred_at,
            }
            for ev in sorted(attempt.proctoring_events, key=lambda x: x.occurred_at)
        ]
    }
