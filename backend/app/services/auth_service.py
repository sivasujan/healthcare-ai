"""Authentication service: registration, login, tokens, sessions, admin seeding."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.auth.security import SecurityService
from app.config import settings
from app.core.exceptions import AuthError, ConflictError, NotFoundError
from app.models import Session as SessionModel
from app.models import User


class AuthService:
    """Business logic for all authentication operations."""

    @staticmethod
    def register(
        db: Session,
        *,
        full_name: str,
        email: str,
        password: str,
        phone: str | None = None,
    ) -> User:
        email = email.lower().strip()
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ConflictError("An account with this email already exists")

        user = User(
            full_name=full_name.strip(),
            email=email,
            hashed_password=SecurityService.hash_password(password),
            phone=phone,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> User:
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if user is None or not SecurityService.verify_password(password, user.hashed_password):
            raise AuthError("Invalid email or password")
        if not user.is_active:
            raise AuthError("Account is deactivated. Contact support.")
        return user

    @staticmethod
    def create_session(
        db: Session,
        user: User,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[str, str]:
        """Create access + refresh tokens and persist the session row."""
        access, access_jti, _ = SecurityService.create_access_token(user.id)
        refresh, refresh_jti, refresh_expires = SecurityService.create_refresh_token(user.id)

        db.add(
            SessionModel(
                user_id=user.id,
                token_id=refresh_jti,
                user_agent=(user_agent or "")[:255],
                ip_address=(ip_address or "")[:64],
                expires_at=refresh_expires,
                is_active=True,
            )
        )
        db.commit()
        return access, refresh

    @staticmethod
    def refresh_tokens(db: Session, refresh_token: str) -> tuple[str, str]:
        payload = SecurityService.decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise AuthError("Invalid refresh token")

        session_row = (
            db.query(SessionModel)
            .filter(
                SessionModel.token_id == payload.get("jti", ""),
                SessionModel.is_active.is_(True),
            )
            .first()
        )
        if session_row is None:
            raise AuthError("Session expired or revoked")

        user = db.query(User).filter(User.id == int(payload["sub"])).first()
        if user is None or not user.is_active:
            raise AuthError("User not found or deactivated")

        access, access_jti, _ = SecurityService.create_access_token(user.id)
        new_refresh, new_jti, new_expires = SecurityService.create_refresh_token(user.id)

        session_row.token_id = new_jti
        session_row.expires_at = new_expires
        db.commit()
        return access, new_refresh

    @staticmethod
    def logout(db: Session, refresh_token: str | None) -> None:
        if not refresh_token:
            return
        payload = SecurityService.decode_token(refresh_token)
        if payload is None:
            return
        session_row = (
            db.query(SessionModel)
            .filter(SessionModel.token_id == payload.get("jti", ""))
            .first()
        )
        if session_row:
            session_row.is_active = False
            db.commit()

    @staticmethod
    def change_password(db: Session, user: User, current: str, new: str) -> None:
        if not SecurityService.verify_password(current, user.hashed_password):
            raise AuthError("Current password is incorrect")
        user.hashed_password = SecurityService.hash_password(new)
        user.updated_at = datetime.now(timezone.utc)
        db.add(user)
        db.commit()

    @staticmethod
    def ensure_admin(db: Session) -> None:
        """Seed the default admin account on startup (if not present)."""
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if admin:
            return
        db.add(
            User(
                full_name="Administrator",
                email=settings.ADMIN_EMAIL,
                hashed_password=SecurityService.hash_password(settings.ADMIN_PASSWORD),
                role="admin",
                is_admin=True,
            )
        )
        db.commit()
