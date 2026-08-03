"""Security primitives for the auth module."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
import jwt

from app.config import settings


class SecurityService:
    """Password hashing and JWT token helpers (single source of truth)."""

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _create_token(
        user_id: int, expires_delta: timedelta, token_type: str
    ) -> tuple[str, str, datetime]:
        now = datetime.now(timezone.utc)
        expires_at = now + expires_delta
        jti = secrets.token_hex(32)
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "type": token_type,
            "iat": now,
            "exp": expires_at,
            "jti": jti,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token, jti, expires_at

    @staticmethod
    def create_access_token(user_id: int) -> tuple[str, str, datetime]:
        return SecurityService._create_token(
            user_id,
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "access",
        )

    @staticmethod
    def create_refresh_token(user_id: int) -> tuple[str, str, datetime]:
        return SecurityService._create_token(
            user_id,
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "refresh",
        )

    @staticmethod
    def decode_token(token: str) -> Optional[dict[str, Any]]:
        try:
            return jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.PyJWTError:
            return None
