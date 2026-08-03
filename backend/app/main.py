"""FastAPI application entry point.

Run with::

    uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger
from app.database import SessionLocal, init_db
from app.middleware.request_logging import RequestLoggingMiddleware
from app.services.auth_service import AuthService
from app.services.medicine_service import seed_medicines

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup: initialize DB, seed admin + knowledge base, shutdown: cleanup."""
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    init_db()
    db = SessionLocal()
    try:
        AuthService.ensure_admin(db)
        seed_medicines(db)
    finally:
        db.close()
    if not settings.OPENROUTER_API_KEY:
        logger.warning(
            "OPENROUTER_API_KEY is not set - AI features will be unavailable. "
            "Copy backend/.env.example to backend/.env and add your key."
        )
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Intelligent Multi-Agent AI Healthcare Assistant - FastAPI backend "
        "with LangGraph agents, OpenRouter model routing, JWT auth and SQLite."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_PREFIX)
