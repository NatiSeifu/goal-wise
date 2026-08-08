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


def test_financial_profile_get_returns_null_when_missing(client: TestClient) -> None:
    _register(client)

    response = client.get("/api/v1/financial-profile")

    assert response.status_code == 200
    assert response.json() == {"item": None}


def test_financial_profile_put_requires_csrf(client: TestClient) -> None:
    _register(client)

    response = client.put("/api/v1/financial-profile", json=_profile_payload())

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_failed"


def test_financial_profile_put_creates_and_replaces(client: TestClient) -> None:
    csrf_token = _register(client)

    create_response = client.put(
        "/api/v1/financial-profile",
        json=_profile_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    replace_response = client.put(
        "/api/v1/financial-profile",
        json={**_profile_payload(), "starting_cash_cents": 125000},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert create_response.status_code == 200
    assert replace_response.status_code == 200
    assert replace_response.json()["item"]["id"] == create_response.json()["item"]["id"]
    assert replace_response.json()["item"]["starting_cash_cents"] == 125000


def test_financial_profile_put_creates_snapshot_when_goal_exists(
    client: TestClient,
    engine: Engine,
) -> None:
    csrf_token = _register(client)
    goal_response = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    assert goal_response.status_code == 201

    profile_response = client.put(
        "/api/v1/financial-profile",
        json=_profile_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )

    snapshots = _snapshots(engine)
    assert profile_response.status_code == 200
    assert len(snapshots) == 1
    assert snapshots[0].trigger == "financial_profile_updated"
    assert snapshots[0].normalized_input_json["goal"]["name"] == "Emergency fund"


def test_unconfirmed_reserve_buffer_does_not_create_snapshot(
    client: TestClient,
    engine: Engine,
) -> None:
    csrf_token = _register(client)
    goal_response = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    assert goal_response.status_code == 201

    profile_response = client.put(
        "/api/v1/financial-profile",
        json={**_profile_payload(), "reserve_buffer_confirmed": False},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert profile_response.status_code == 200
    assert _snapshots(engine) == []


def test_income_source_crud_uses_active_list_and_soft_delete(client: TestClient) -> None:
    csrf_token = _register(client)

    create_response = client.post(
        "/api/v1/income-sources",
        json=_income_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    income_id = create_response.json()["item"]["id"]
    list_response = client.get("/api/v1/income-sources")
    patch_response = client.patch(
        f"/api/v1/income-sources/{income_id}",
        json={**_income_payload(), "confidence": "unconfirmed"},
        headers={"X-CSRF-Token": csrf_token},
    )
    delete_response = client.delete(
        f"/api/v1/income-sources/{income_id}",
        headers={"X-CSRF-Token": csrf_token},
    )
    list_after_delete = client.get("/api/v1/income-sources")

    assert create_response.status_code == 201
    assert list_response.json()["items"][0]["id"] == income_id
    assert patch_response.status_code == 200
    assert patch_response.json()["item"]["confidence"] == "unconfirmed"
    assert delete_response.status_code == 204
    assert list_after_delete.json() == {"items": []}


def test_income_source_write_creates_snapshot_when_inputs_complete(
    client: TestClient,
    engine: Engine,
) -> None:
    csrf_token = _complete_required_setup(client)

    create_response = client.post(
        "/api/v1/income-sources",
        json=_income_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )

    snapshots = _snapshots(engine)
    assert create_response.status_code == 201
    assert [snapshot.trigger for snapshot in snapshots] == [
        "income_source_created",
        "financial_profile_updated",
    ]


def test_income_source_validation_errors_use_field_envelope(client: TestClient) -> None:
    csrf_token = _register(client)

    response = client.post(
        "/api/v1/income-sources",
        json={**_income_payload(), "amount_cents": 0, "frequency": "daily"},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 422
    assert response.json()["error"]["fields"]["amount_cents"] == ["Must be greater than zero."]
    assert response.json()["error"]["fields"]["frequency"] == [
        "Must be one of: one_time, weekly, biweekly, monthly."
    ]


def test_planned_expense_crud_uses_active_list_and_soft_delete(client: TestClient) -> None:
    csrf_token = _register(client)

    create_response = client.post(
        "/api/v1/planned-expenses",
        json=_expense_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    expense_id = create_response.json()["item"]["id"]
    list_response = client.get("/api/v1/planned-expenses")
    patch_response = client.patch(
        f"/api/v1/planned-expenses/{expense_id}",
        json={**_expense_payload(), "classification": "discretionary"},
        headers={"X-CSRF-Token": csrf_token},
    )
    delete_response = client.delete(
        f"/api/v1/planned-expenses/{expense_id}",
        headers={"X-CSRF-Token": csrf_token},
    )
    list_after_delete = client.get("/api/v1/planned-expenses")

    assert create_response.status_code == 201
    assert list_response.json()["items"][0]["id"] == expense_id
    assert patch_response.status_code == 200
    assert patch_response.json()["item"]["classification"] == "discretionary"
    assert delete_response.status_code == 204
    assert list_after_delete.json() == {"items": []}


def test_planned_expense_delete_creates_snapshot_when_inputs_complete(
    client: TestClient,
    engine: Engine,
) -> None:
    csrf_token = _complete_required_setup(client)
    create_response = client.post(
        "/api/v1/planned-expenses",
        json=_expense_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    expense_id = create_response.json()["item"]["id"]

    delete_response = client.delete(
        f"/api/v1/planned-expenses/{expense_id}",
        headers={"X-CSRF-Token": csrf_token},
    )

    snapshots = _snapshots(engine)
    assert delete_response.status_code == 204
    assert [snapshot.trigger for snapshot in snapshots] == [
        "planned_expense_deactivated",
        "planned_expense_created",
        "financial_profile_updated",
    ]


def test_planned_expense_cross_user_delete_returns_404(client: TestClient) -> None:
    owner_csrf = _register(client, email="owner@example.com")
    create_response = client.post(
        "/api/v1/planned-expenses",
        json=_expense_payload(),
        headers={"X-CSRF-Token": owner_csrf},
    )
    expense_id = create_response.json()["item"]["id"]

    client.cookies.clear()
    other_csrf = _register(client, email="other@example.com")

    response = client.delete(
        f"/api/v1/planned-expenses/{expense_id}",
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


def _profile_payload() -> dict[str, object]:
    return {
        "starting_cash_cents": 120000,
        "balance_as_of_date": "2026-08-07",
        "reserve_buffer_cents": 5000,
        "reserve_buffer_confirmed": True,
    }


def _goal_payload() -> dict[str, object]:
    return {
        "name": "Emergency fund",
        "target_cents": 300000,
        "initial_saved_cents": 50000,
        "current_saved_cents": 75000,
        "start_date": "2026-08-01",
        "target_date": "2026-12-31",
    }


def _complete_required_setup(client: TestClient) -> str:
    csrf_token = _register(client)
    goal_response = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    assert goal_response.status_code == 201
    profile_response = client.put(
        "/api/v1/financial-profile",
        json=_profile_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    assert profile_response.status_code == 200
    return csrf_token


def _income_payload() -> dict[str, object]:
    return {
        "name": "Campus job",
        "amount_cents": 45000,
        "next_date": "2026-08-14",
        "frequency": "weekly",
        "confidence": "confirmed",
    }


def _expense_payload() -> dict[str, object]:
    return {
        "name": "Rent",
        "amount_cents": 90000,
        "next_date": "2026-09-01",
        "frequency": "monthly",
        "classification": "essential",
    }


def _snapshots(engine: Engine) -> list[CalculationSnapshot]:
    with Session(engine) as db_session:
        return list(
            db_session.scalars(
                select(CalculationSnapshot).order_by(
                    CalculationSnapshot.calculated_at.desc(),
                    CalculationSnapshot.id.desc(),
                ),
            ),
        )
