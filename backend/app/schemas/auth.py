"""
Pydantic schemas for authentication and user management.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)


class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.STUDENT


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class StudentProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    college: Optional[str]
    department: Optional[str]
    graduation_year: Optional[int]
    phone: Optional[str]
    bio: Optional[str]
    total_score: float
    aptitude_score: float
    coding_score: float
    streak_days: int
    last_active: Optional[datetime]
    user: UserOut


class TrainerProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    specialization: Optional[str]
    experience_years: Optional[int]
    phone: Optional[str]
    bio: Optional[str]
    user: UserOut


class BatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    member_count: Optional[int] = None


class BatchCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    message: str
