"""Doctor recommendation Pydantic schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class DoctorRecommendRequest(BaseModel):
    symptoms: str = Field(min_length=3, max_length=4000)
    age: Optional[int] = Field(default=None, ge=0, le=130)
    gender: Optional[str] = Field(default=None, max_length=20)
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None


class DoctorRecommendationResult(BaseModel):
    specialty: str
    reason: str
    consultation_type: str
    urgency: str
    preparation_tips: list[str]
    nearby_hospitals: list[str]
    disclaimer: str
    model: str
