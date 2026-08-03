"""Global exception hierarchy and FastAPI exception handlers."""

from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error with an HTTP status code and message."""

    status_code: int = 400

    def __init__(self, message: str = "Something went wrong", status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class NotFoundError(AppError):
    status_code = 404


class AuthError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class ConflictError(AppError):
    status_code = 409


class RateLimitError(AppError):
    status_code = 429


class ModelTimeoutError(AppError):
    """Raised when the AI provider times out; triggers fallback logic."""

    status_code = 503


class ModelProviderError(AppError):
    """Raised when the AI provider fails after all retries."""

    status_code = 502


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app."""

    def _error(message: str, code: int, errors: Any = None) -> JSONResponse:
        return JSONResponse(
            status_code=code,
            content={
                "success": False,
                "message": message,
                "errors": errors,
                "status_code": code,
            },
        )

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return _error(exc.message, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = []
        for err in exc.errors():
            details.append(
                {"field": ".".join(str(x) for x in err.get("loc", [])), "message": err.get("msg")}
            )
        return _error("Validation failed", status.HTTP_422_UNPROCESSABLE_ENTITY, details)

    @app.exception_handler(Exception)
    async def unhandled_handler(_request: Request, exc: Exception) -> JSONResponse:
        return _error(f"Internal server error: {type(exc).__name__}", 500)
