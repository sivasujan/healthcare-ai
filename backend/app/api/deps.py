"""Shared API dependencies."""

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.core.rate_limit import rate_limiter
from app.core.exceptions import RateLimitError
from app.database import get_db
from app.models import User

RateLimitDep = None  # placeholder, replaced below


def enforce_rate_limit(request: Request) -> None:
    """Dependency applying the per-IP rate limit to a route."""
    key = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(key):
        raise RateLimitError("Too many requests. Please try again shortly.")


def get_db_dep() -> Session:
    """Alias of :func:`get_db` for import clarity in routers."""
    return next(get_db())


__all__ = ["get_db", "get_current_user", "User", "enforce_rate_limit", "get_db_dep"]
