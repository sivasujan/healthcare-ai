"""Symptom analysis Pydantic schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class SymptomAnalyzeRequest(BaseModel):
    symptoms: str = Field(min_length=3, max_length=4000)
    age: Optional[int] = Field(default=None, ge=0, le=130)
    gender: Optional[str] = Field(default=None, max_length=20)
    height_cm: Optional[float] = Field(default=None, gt=0, le=300)
    weight_kg: Optional[float] = Field(default=None, gt=0, le=500)
    duration: Optional[str] = Field(default=None, max_length=200)
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    allergies: Optional[str] = None
    lifestyle: Optional[str] = None
    smoking: Optional[str] = None
    alcohol: Optional[str] = None
    exercise: Optional[str] = None


class Condition(BaseModel):
    name: str
    confidence: float
    severity: str


class Recommendation(BaseModel):
    title: str
    detail: str


class SymptomAnalysisResult(BaseModel):
    possible_conditions: list[Condition]
    overall_severity: str
    recommendations: list[Recommendation]
    precautions: list[str]
    doctor_specialty: str
    doctor_reason: str
    emergency_detected: bool
    emergency_instructions: Optional[list[str]] = None
    disclaimer: str
    model: str
