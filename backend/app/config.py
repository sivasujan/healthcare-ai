"""Application configuration via pydantic-settings.

All environment variables are read from ``backend/.env`` (or the process
environment) and validated at import time.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central configuration object for the whole backend application."""

    # --- General ---
    APP_NAME: str = "Intelligent Multi-Agent AI Healthcare Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    # --- Security ---
    SECRET_KEY: str = "change-me-in-production-9f8e7d6c5b4a3f2e1d0c"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8

    # --- Database ---
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'healthcare.db'}"

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # --- Rate limiting ---
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # --- AI / OpenRouter ---
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_SITE_URL: str = "http://localhost:3000"
    OPENROUTER_SITE_NAME: str = "HealthCare Assistant"

    PRIMARY_MODEL: str = "openai/gpt-4o"
    SECONDARY_MODEL: str = "anthropic/claude-3.5-sonnet"
    FALLBACK_MODEL: str = "google/gemini-1.5-flash"
    FREE_MODEL: str = "google/gemma-2-9b-it:free"

    AI_TIMEOUT_SECONDS: int = 60
    AI_MAX_RETRIES: int = 2
    AI_TEMPERATURE: float = 0.4
    AI_MAX_TOKENS: int = 2048

    # --- Admin ---
    ADMIN_EMAIL: str = "admin@healthcare.local"
    ADMIN_PASSWORD: str = "Admin@12345"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings singleton."""
    return Settings()


settings = get_settings()
