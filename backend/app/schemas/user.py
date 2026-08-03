"""User profile related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.auth import UserPublic


class HealthProfile(BaseModel):
    age: Optional[int] = Field(default=None, ge=0, le=130)
    gender: Optional[str] = Field(default=None, max_length=20)
    height_cm: Optional[float] = Field(default=None, gt=0, le=300)
    weight_kg: Optional[float] = Field(default=None, gt=0, le=500)
    blood_group: Optional[str] = Field(default=None, max_length=10)
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    phone: Optional[str] = Field(default=None, max_length=20)
    preferred_language: Optional[str] = Field(default=None, max_length=20)
    dark_mode: Optional[bool] = None
    profile: Optional[HealthProfile] = None


class ProfileResponse(UserPublic):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    is_admin: bool
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    blood_group: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    preferred_language: str = "en"
    dark_mode: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
