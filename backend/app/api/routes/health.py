"""Health check API route."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.common import ApiResponse, HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=ApiResponse[HealthResponse])
def health_check(db: Session = Depends(get_db)) -> ApiResponse[HealthResponse]:
    """Liveness + database connectivity check."""
    db.execute(text("SELECT 1"))
    return ApiResponse(
        success=True,
        data=HealthResponse(
            status="ok",
            version=settings.APP_VERSION,
            database="connected",
        ),
    )
