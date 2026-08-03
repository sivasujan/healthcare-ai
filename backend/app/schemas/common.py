"""Shared Pydantic schemas (envelopes, pagination, health)."""

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API envelope: ``{"success": true, "data": ..., "message": ...}``."""

    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
