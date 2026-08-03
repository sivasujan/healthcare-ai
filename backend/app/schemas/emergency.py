"""Emergency detection Pydantic schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class EmergencyCheckRequest(BaseModel):
    symptoms: str = Field(min_length=3, max_length=4000)
    age: Optional[int] = Field(default=None, ge=0, le=130)
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None


class EmergencyCheckResult(BaseModel):
    emergency_detected: bool
    severity: str
    conditions: list[str]
    instructions: list[str]
    immediate_actions: list[str]
    nearby_hospitals: list[str]
    emergency_number: str
    disclaimer: str
    model: str
