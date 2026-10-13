"""
API router — aggregates all route modules.
"""
from fastapi import APIRouter
from app.api.routes import auth, student, trainer, proctoring, coding, student_ai

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(student.router)
api_router.include_router(student_ai.router)
api_router.include_router(trainer.router)
api_router.include_router(proctoring.router)
api_router.include_router(coding.router)
