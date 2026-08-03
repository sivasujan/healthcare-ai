"""Authentication API routes."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import enforce_rate_limit
from app.auth import get_current_user
from app.auth.security import SecurityService
from app.config import settings
from app.core.exceptions import AuthError
from app.core.logging import client_ip
from app.database import get_db
from app.models import User
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    UserPublic,
)
from app.schemas.common import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _build_auth_response(db: Session, user: User, request: Request) -> AuthResponse:
    access, refresh = AuthService.create_session(
        db,
        user,
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip(request),
    )
    return AuthResponse(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserPublic.model_validate(user),
    )


@router.post(
    "/register",
    response_model=ApiResponse[AuthResponse],
    status_code=201,
    dependencies=[Depends(enforce_rate_limit)],
)
def register(
    payload: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ApiResponse[AuthResponse]:
    """Create a new user account and return tokens."""
    user = AuthService.register(
        db,
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
        phone=payload.phone,
    )
    return ApiResponse(
        success=True,
        message="Account created successfully",
        data=_build_auth_response(db, user, request),
    )


@router.post(
    "/login",
    response_model=ApiResponse[AuthResponse],
    dependencies=[Depends(enforce_rate_limit)],
)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ApiResponse[AuthResponse]:
    """Authenticate with email and password; returns JWT tokens."""
    user = AuthService.authenticate(db, payload.email, payload.password)
    return ApiResponse(
        success=True,
        message="Logged in successfully",
        data=_build_auth_response(db, user, request),
    )


@router.post("/refresh", response_model=ApiResponse[AuthResponse])
def refresh(
    payload: RefreshRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ApiResponse[AuthResponse]:
    """Exchange a valid refresh token for a new token pair."""
    access, new_refresh = AuthService.refresh_tokens(db, payload.refresh_token)

    payload_data = SecurityService.decode_token(access)
    if payload_data is None:
        raise AuthError("Invalid token")
    user = db.get(User, int(payload_data["sub"]))
    if user is None:
        raise AuthError("User not found")

    return ApiResponse(
        success=True,
        message="Tokens refreshed",
        data=AuthResponse(
            access_token=access,
            refresh_token=new_refresh,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserPublic.model_validate(user),
        ),
    )


@router.post("/logout", response_model=ApiResponse[None])
def logout(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> ApiResponse[None]:
    """Revoke the active session."""
    AuthService.logout(db, payload.refresh_token)
    return ApiResponse(success=True, message="Logged out successfully")


@router.post("/forgot-password", response_model=ApiResponse[None])
def forgot_password(
    payload: ForgotPasswordRequest,
    _db: Session = Depends(get_db),
) -> ApiResponse[None]:
    """Request a password reset.

    Demo behavior: always returns success to avoid user enumeration attacks.
    A production system would email a tokenized reset link.
    """
    return ApiResponse(
        success=True,
        message="If that email exists, a reset link would be sent (demo mode).",
    )


@router.post("/reset-password", response_model=ApiResponse[None])
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[None]:
    """Reset a password directly.

    Demo mode: requires no token. Production should use a signed reset token.
    """
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if user:
        from app.auth.security import SecurityService

        user.hashed_password = SecurityService.hash_password(payload.new_password)
        db.add(user)
        db.commit()
    return ApiResponse(success=True, message="Password reset successfully")
