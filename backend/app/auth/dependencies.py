"""Authentication module: FastAPI dependencies for protected routes."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.auth.security import SecurityService
from app.config import settings
from app.core.exceptions import AuthError
from app.core.rate_limit import rate_limiter
from app.database import get_db
from app.models import Session as SessionModel
from app.models import User


class AuthService:
    """Helpers for JWT auth flow used by route dependencies."""

    @staticmethod
    def _get_payload(request: Request, db: Session) -> dict:
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise AuthError("Missing or malformed Authorization header")
        token = header[7:]
        payload = SecurityService.decode_token(token)
        if payload is None:
            raise AuthError("Invalid or expired token")
        if payload.get("type") != "access":
            raise AuthError("Token type must be 'access'")
        return payload

    @staticmethod
    def get_current_user(
        request: Request, db: Session = Depends(get_db)
    ) -> User:
        """Resolve the authenticated user from the bearer token."""
        payload = AuthService._get_payload(request, db)
        try:
            user_id = int(payload["sub"])
        except (KeyError, ValueError):
            raise AuthError("Invalid token subject")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            raise AuthError("User not found or deactivated")
        return user

    @staticmethod
    def get_current_admin(
        request: Request, db: Session = Depends(get_db)
    ) -> User:
        """Resolve the authenticated user and require the admin role."""
        user = AuthService.get_current_user(request, db)
        if not user.is_admin:
            raise AuthError("Administrator privileges required", status_code=403)
        return user

    @staticmethod
    def check_rate_limit(request: Request, db: Session) -> None:
        """Apply the per-IP sliding window rate limit."""
        key = request.client.host if request.client else "unknown"
        if not rate_limiter.is_allowed(key):
            raise AuthError(
                "Too many requests, please slow down",
                status_code=429,
            )


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency: current authenticated user."""
    return AuthService.get_current_user(request, db)


def get_current_admin(
    request: Request, db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency: current authenticated admin."""
    return AuthService.get_current_admin(request, db)
