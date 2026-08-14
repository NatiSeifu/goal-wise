from collections.abc import Generator

import pytest
from app.api.constants import SESSION_COOKIE_NAME
from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db_session, make_engine, make_session_factory
from app.main import app
from app.models import CalculationSnapshot
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
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
        return Settings(environment="test", session_secret=TEST_SESSION_SECRET)

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[get_settings] = override_settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_active_goal_requires_auth(client: TestClient) -> None:
    response = client.get("/api/v1/goals/active")

    assert response.status_code == 401


def test_get_active_goal_returns_null_when_missing(client: TestClient) -> None:
    _register(client)

    response = client.get("/api/v1/goals/active")

    assert response.status_code == 200
    assert response.json() == {"item": None}


def test_create_goal_requires_csrf(client: TestClient) -> None:
    _register(client)

    response = client.post("/api/v1/goals", json=_goal_payload())

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_failed"


def test_create_and_get_active_goal(client: TestClient) -> None:
    csrf_token = _register(client)

    create_response = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    get_response = client.get("/api/v1/goals/active")

    assert create_response.status_code == 201
    assert create_response.json()["item"]["name"] == "Emergency fund"
    assert create_response.json()["item"]["status"] == "active"
    assert get_response.status_code == 200
    assert get_response.json()["item"]["id"] == create_response.json()["item"]["id"]


def test_create_goal_without_profile_does_not_create_snapshot(
    client: TestClient,
    engine: Engine,
) -> None:
    csrf_token = _register(client)

    response = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 201
    assert _snapshot_count(engine) == 0


def test_create_goal_validation_errors_use_field_envelope(client: TestClient) -> None:
    csrf_token = _register(client)

    response = client.post(
        "/api/v1/goals",
        json={**_goal_payload(), "target_cents": 0, "target_date": "2026-08-07"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["error"]["fields"]["target_cents"] == ["Must be greater than zero."]
    assert response.json()["error"]["fields"]["target_date"] == [
        "Must be after the user's current local date."
    ]


def test_patch_goal_returns_404_for_cross_user_access(client: TestClient) -> None:
    owner_csrf = _register(client, email="owner@example.com")
    create_response = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": owner_csrf},
    )
    goal_id = create_response.json()["item"]["id"]

    client.cookies.clear()
    other_csrf = _register(client, email="other@example.com")

    response = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={**_goal_payload(), "name": "Other user update"},
        headers={"X-CSRF-Token": other_csrf},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_patch_goal_marks_completed(client: TestClient) -> None:
    csrf_token = _register(client)
    create_response = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    goal_id = create_response.json()["item"]["id"]

    response = client.patch(
        f"/api/v1/goals/{goal_id}",
        json={**_goal_payload(), "current_saved_cents": 300000},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 200
    assert response.json()["item"]["status"] == "completed"
    assert client.get("/api/v1/goals/active").json() == {"item": None}


def test_archive_goal_requires_csrf(client: TestClient) -> None:
    csrf_token = _register(client)
    create_response = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    goal_id = create_response.json()["item"]["id"]

    response = client.post(f"/api/v1/goals/{goal_id}/archive")

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_failed"


def test_archive_goal_marks_goal_archived_and_clears_active_goal(
    client: TestClient,
) -> None:
    csrf_token = _register(client)
    create_response = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    goal_id = create_response.json()["item"]["id"]

    archive_response = client.post(
        f"/api/v1/goals/{goal_id}/archive",
        headers={"X-CSRF-Token": csrf_token},
    )

    assert archive_response.status_code == 200
    assert archive_response.json()["item"]["id"] == goal_id
    assert archive_response.json()["item"]["status"] == "archived"
    assert archive_response.json()["item"]["archived_at"] is not None
    assert client.get("/api/v1/goals/active").json() == {"item": None}


def test_archive_goal_allows_new_active_goal(client: TestClient) -> None:
    csrf_token = _register(client)
    create_response = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    goal_id = create_response.json()["item"]["id"]
    archive_response = client.post(
        f"/api/v1/goals/{goal_id}/archive",
        headers={"X-CSRF-Token": csrf_token},
    )

    new_goal_response = client.post(
        "/api/v1/goals",
        json={**_goal_payload(), "name": "Move fund"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert archive_response.status_code == 200
    assert new_goal_response.status_code == 201
    assert new_goal_response.json()["item"]["name"] == "Move fund"
    assert new_goal_response.json()["item"]["status"] == "active"


def test_archive_goal_returns_404_for_cross_user_access(client: TestClient) -> None:
    owner_csrf = _register(client, email="archive-owner@example.com")
    create_response = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": owner_csrf},
    )
    goal_id = create_response.json()["item"]["id"]

    client.cookies.clear()
    other_csrf = _register(client, email="archive-other@example.com")

    response = client.post(
        f"/api/v1/goals/{goal_id}/archive",
        headers={"X-CSRF-Token": other_csrf},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


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


def _goal_payload() -> dict[str, object]:
    return {
        "name": "Emergency fund",
        "target_cents": 300000,
        "initial_saved_cents": 50000,
        "current_saved_cents": 75000,
        "start_date": "2026-08-01",
        "target_date": "2026-12-31",
    }


def _snapshot_count(engine: Engine) -> int:
    with Session(engine) as db_session:
        return len(list(db_session.scalars(select(CalculationSnapshot))))
