"""Pytest fixtures: isolated test database and mocked model router."""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.ai.model_router import ModelCall, ModelProviderError  # noqa: E402

TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TEST_SESSION = sessionmaker(bind=TEST_ENGINE, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield


@pytest.fixture()
def db():
    """Fresh database session per test (rolled back at the end)."""
    connection = TEST_ENGINE.connect()
    transaction = connection.begin()
    session = TEST_SESSION(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """TestClient with the dependency-overridden database."""

    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_model_call(content: str, model: str = "test/free-model") -> ModelCall:
    return ModelCall(
        content=content,
        model=model,
        tier="primary",
        prompt_tokens=10,
        completion_tokens=50,
        latency_ms=100.0,
        cost_usd=0.0,
    )


@pytest.fixture()
def mock_router(monkeypatch):
    """Replace the singleton router with canned responses per intent."""

    def _install(responses: dict):
        def fake_chat(messages, **kwargs):
            system = messages[0]["content"].lower() if messages else ""
            user = messages[-1]["content"].lower() if len(messages) > 1 else ""
            combined = f"{system} {user}"
            for key, content in responses.items():
                if key.replace("_", " ") in combined:
                    return make_model_call(content)
            if len(responses) == 1:
                return make_model_call(next(iter(responses.values())))
            return make_model_call("generic mock response")

        monkeypatch.setattr("app.ai.model_router.router.chat", fake_chat)

    return _install
