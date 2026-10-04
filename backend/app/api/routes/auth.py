"""
Authentication routes: register, login, refresh, logout, me.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User, UserRole, StudentProfile, TrainerProfile
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut, RefreshTokenRequest, MessageResponse
from app.api.deps import get_current_user
import logging

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check email uniqueness
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.flush()  # Get user.id

    # Create role-specific profile
    if payload.role == UserRole.STUDENT:
        db.add(StudentProfile(user_id=user.id))
    elif payload.role == UserRole.TRAINER:
        db.add(TrainerProfile(user_id=user.id))

    await db.commit()
    await db.refresh(user)

    tokens = _generate_tokens(user)
    logger.info(f"New user registered: {user.email} ({user.role})")
    return {**tokens, "user": UserOut.model_validate(user)}


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    tokens = _generate_tokens(user)
    logger.info(f"User logged in: {user.email}")
    return {**tokens, "user": UserOut.model_validate(user)}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    data = decode_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    result = await db.execute(select(User).where(User.id == int(data["sub"])))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    tokens = _generate_tokens(user)
    return {**tokens, "user": UserOut.model_validate(user)}


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    # JWT is stateless; client should discard tokens.
    # For production, implement a token denylist.
    return {"message": "Logged out successfully"}


def _generate_tokens(user: User) -> dict:
    data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
    return {
        "access_token": create_access_token(data),
        "refresh_token": create_refresh_token(data),
        "token_type": "bearer",
    }
