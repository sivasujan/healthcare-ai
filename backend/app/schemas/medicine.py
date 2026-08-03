"""Medicine information Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MedicineSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=300)


class MedicineOut(BaseModel):
    id: int
    name: str
    generic_name: Optional[str] = None
    category: Optional[str] = None
    purpose: Optional[str] = None
    uses: Optional[str] = None
    dosage: Optional[str] = None
    warnings: Optional[str] = None
    side_effects: Optional[str] = None
    interactions: Optional[str] = None
    storage: Optional[str] = None
    notes: Optional[str] = None
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MedicineSearchResult(BaseModel):
    medicine: Optional[MedicineOut] = None
    summary: Optional[str] = None
    disclaimer: str
    model: str


class SavedMedicineOut(BaseModel):
    id: int
    medicine_id: int
    name: str
    category: Optional[str] = None
    purpose: Optional[str] = None
    saved_at: datetime

    model_config = {"from_attributes": True}
