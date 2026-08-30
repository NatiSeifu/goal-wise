from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from app.api.constants import SESSION_COOKIE_NAME
from app.api.dependencies import get_ai_provider, utc_now
from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db_session, make_engine, make_session_factory
from app.main import app
from app.services.ai_provider import AiProviderError, FakeAiProvider
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session

TEST_SESSION_SECRET = "test-session-secret"


@pytest.fixture
def engine() -> Engine:
    sqlite_engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(sqlite_engine)
    return sqlite_engine


@pytest.fixture
def client(engine: Engine) -> Generator[TestClient, None, None]:
    session_factory = make_session_factory(engine)

    def override_db_session() -> Generator[Session, None, None]:
        with session_factory() as db_session:
            yield db_session

    def override_settings() -> Settings:
        return Settings(
            environment="test",
            session_secret=TEST_SESSION_SECRET,
            ai_summary_enabled=False,
            groq_api_key=None,
            _env_file=None,
        )

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[get_settings] = override_settings
    app.dependency_overrides[utc_now] = lambda: datetime(2026, 8, 29, 12, 0, tzinfo=UTC)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_explanation_request_requires_authentication(client: TestClient) -> None:
    response = client.post("/api/v1/ai-explanations/latest")

    assert response.status_code == 401


def test_explanation_status_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/ai-explanations/status")

    assert response.status_code == 401


def test_explanation_status_is_disabled_by_default(client: TestClient) -> None:
    _register(client)

    response = client.get("/api/v1/ai-explanations/status")

    assert response.status_code == 200
    assert response.json() == {"enabled": False}


def test_explanation_request_requires_csrf(client: TestClient) -> None:
    _register(client)

    response = client.post("/api/v1/ai-explanations/latest")

    assert response.status_code == 403


def test_explanation_request_returns_not_found_without_snapshot(client: TestClient) -> None:
    csrf_token = _register(client)

    response = client.post(
        "/api/v1/ai-explanations/latest",
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "calculation_snapshot_not_found",
            "message": "No calculation snapshot is available to explain.",
        }
    }


def test_disabled_request_returns_unavailable_and_does_not_call_provider(
    client: TestClient,
) -> None:
    csrf_token = _complete_required_setup(client)
    provider = FakeAiProvider(response=_valid_response())
    app.dependency_overrides[get_ai_provider] = lambda: provider

    response = client.post(
        "/api/v1/ai-explanations/latest",
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "ai_explanation_unavailable",
            "message": "We could not prepare an explanation right now. Please try again later.",
        }
    }
    assert provider.calls == []


def test_provider_failure_returns_generic_unavailable_error(
    client: TestClient,
) -> None:
    csrf_token = _complete_required_setup(client)
    app.dependency_overrides[get_ai_provider] = lambda: FakeAiProvider(
        error=AiProviderError("provider failed")
    )
    app.dependency_overrides[get_settings] = lambda: Settings(
        environment="test",
        session_secret=TEST_SESSION_SECRET,
        ai_summary_enabled=True,
        groq_api_key="test-key",
    )

    response = client.post(
        "/api/v1/ai-explanations/latest",
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "ai_explanation_unavailable",
            "message": "We could not prepare an explanation right now. Please try again later.",
        }
    }


def test_enabled_request_returns_generated_explanation_and_reuses_it(
    client: TestClient,
) -> None:
    csrf_token = _complete_required_setup(client)
    provider = FakeAiProvider(response=_valid_response())
    app.dependency_overrides[get_ai_provider] = lambda: provider
    app.dependency_overrides[get_settings] = lambda: Settings(
        environment="test",
        session_secret=TEST_SESSION_SECRET,
        ai_summary_enabled=True,
        groq_api_key="test-key",
    )

    first = client.post(
        "/api/v1/ai-explanations/latest",
        headers={"X-CSRF-Token": csrf_token},
    )
    second = client.post(
        "/api/v1/ai-explanations/latest",
        headers={"X-CSRF-Token": csrf_token},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["enabled"] is True
    assert first.json()["item"]["source"] == "generated"
    assert second.json()["item"]["source"] == "generated"
    assert first.json()["item"]["snapshot_id"] == second.json()["item"]["snapshot_id"]
    assert len(provider.calls) == 1


def _register(client: TestClient, *, email: str = "nati@example.com") -> str:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "correct horse battery staple",
            "time_zone": "America/Los_Angeles",
        },
    )
    assert response.status_code == 201
    assert client.cookies.get(SESSION_COOKIE_NAME)
    return str(response.json()["item"]["csrf_token"])


def _complete_required_setup(client: TestClient) -> str:
    csrf_token = _register(client)
    goal_response = client.post(
        "/api/v1/goals",
        json={
            "name": "Emergency fund",
            "target_cents": 300000,
            "initial_saved_cents": 50000,
            "current_saved_cents": 75000,
            "start_date": "2026-08-01",
            "target_date": "2026-12-31",
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    assert goal_response.status_code == 201
    profile_response = client.put(
        "/api/v1/financial-profile",
        json={
            "starting_cash_cents": 120000,
            "balance_as_of_date": "2026-08-07",
            "reserve_buffer_cents": 5000,
            "reserve_buffer_confirmed": True,
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    assert profile_response.status_code == 200
    income_response = client.post(
        "/api/v1/income-sources",
        json={
            "name": "Campus job",
            "amount_cents": 45000,
            "next_date": "2026-08-14",
            "frequency": "weekly",
            "confidence": "confirmed",
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    assert income_response.status_code == 201
    return csrf_token


def _valid_response() -> dict[str, object]:
    return {
        "schema_version": "ai-explanation-v1",
        "headline": "Your plan is on track",
        "body": "Your current plan leaves room for weekly spending while keeping the goal in view.",
        "observations": [],
        "next_step": "Keep your planned expenses up to date.",
    }
