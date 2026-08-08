from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from app.api.constants import SESSION_COOKIE_NAME
from app.api.dependencies import utc_now
from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db_session, make_engine, make_session_factory
from app.main import app
from app.models import CalculationSnapshot, WeeklyPlan
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

    now_counter = 0

    def override_utc_now() -> datetime:
        nonlocal now_counter
        value = datetime(2026, 8, 8, 12, 0, now_counter, tzinfo=UTC)
        now_counter += 1
        return value

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[get_settings] = override_settings
    app.dependency_overrides[utc_now] = override_utc_now
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_latest_snapshot_requires_auth(client: TestClient) -> None:
    response = client.get("/api/v1/calculation-snapshots/latest")

    assert response.status_code == 401


def test_latest_snapshot_returns_null_when_missing(client: TestClient) -> None:
    _register(client)

    response = client.get("/api/v1/calculation-snapshots/latest")

    assert response.status_code == 200
    assert response.json() == {"item": None}


def test_latest_snapshot_returns_latest_user_owned_snapshot(client: TestClient) -> None:
    owner_csrf = _complete_required_setup(client, email="owner@example.com")
    owner_snapshot_response = client.get("/api/v1/calculation-snapshots/latest")
    owner_snapshot_id = owner_snapshot_response.json()["item"]["id"]

    client.post(
        "/api/v1/income-sources",
        json=_income_payload(),
        headers={"X-CSRF-Token": owner_csrf},
    )
    latest_owner_response = client.get("/api/v1/calculation-snapshots/latest")

    client.cookies.clear()
    _register(client, email="other@example.com")
    other_response = client.get("/api/v1/calculation-snapshots/latest")

    assert latest_owner_response.status_code == 200
    assert latest_owner_response.json()["item"]["id"] != owner_snapshot_id
    assert latest_owner_response.json()["item"]["trigger"] == "income_source_created"
    assert other_response.status_code == 200
    assert other_response.json() == {"item": None}


def test_dashboard_requires_auth(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard")

    assert response.status_code == 401


def test_dashboard_returns_setup_required_before_snapshot_exists(
    client: TestClient,
) -> None:
    _register(client)

    response = client.get("/api/v1/dashboard")

    assert response.status_code == 200
    assert response.json() == {
        "item": {
            "status": "setup_required",
            "missing_inputs": ["active_goal", "financial_profile"],
            "snapshot_id": None,
            "calculated_at": None,
            "formula_version": None,
            "goal": None,
            "pace": None,
            "explanation": None,
            "changed_from_previous": None,
        }
    }


def test_dashboard_returns_values_from_latest_snapshot(
    client: TestClient,
    engine: Engine,
) -> None:
    csrf_token = _complete_required_setup(client)
    client.post(
        "/api/v1/income-sources",
        json=_income_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    snapshot_count_before = _snapshot_count(engine)
    latest_snapshot = _latest_snapshot(engine)
    snapshot_outputs = latest_snapshot.result_json["outputs"]
    snapshot_goal = latest_snapshot.normalized_input_json["goal"]

    response = client.get("/api/v1/dashboard")

    body = response.json()["item"]
    assert response.status_code == 200
    assert body["status"] == "ready"
    assert body["missing_inputs"] == []
    assert body["snapshot_id"] == latest_snapshot.id
    assert body["formula_version"] == latest_snapshot.formula_version
    assert body["goal"] == {
        "id": snapshot_goal["id"],
        "name": snapshot_goal["name"],
        "target_cents": snapshot_goal["target_cents"],
        "current_saved_cents": snapshot_goal["current_saved_cents"],
        "target_date": snapshot_goal["target_date"],
    }
    assert body["pace"]["weekly_safe_to_spend_cents"] == snapshot_outputs[
        "weekly_safe_to_spend_cents"
    ]
    assert body["pace"]["projected_shortfall_cents"] == snapshot_outputs[
        "projected_shortfall_cents"
    ]
    assert body["pace"]["remaining_weeks"] == snapshot_outputs["remaining_weeks"]
    assert body["pace"]["progress_percentage"] == snapshot_outputs["progress_percentage"]
    assert body["pace"]["pace_status"] == snapshot_outputs["pace_status"]
    assert body["explanation"] == latest_snapshot.result_json["explanation"]
    assert body["changed_from_previous"] == latest_snapshot.result_json[
        "changed_from_previous"
    ]
    assert _snapshot_count(engine) == snapshot_count_before
    weekly_plans = _weekly_plans(engine)
    assert len(weekly_plans) == 1
    assert weekly_plans[0].created_from_snapshot_id == latest_snapshot.id


def test_dashboard_does_not_replace_current_week_opening_allowance(
    client: TestClient,
    engine: Engine,
) -> None:
    csrf_token = _complete_required_setup(client)
    first_dashboard = client.get("/api/v1/dashboard")
    first_plan = _weekly_plans(engine)[0]
    first_opening_allowance = first_dashboard.json()["item"]["pace"][
        "current_week_opening_allowance_cents"
    ]

    client.post(
        "/api/v1/income-sources",
        json=_income_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    latest_snapshot = _latest_snapshot(engine)
    second_dashboard = client.get("/api/v1/dashboard")

    body = second_dashboard.json()["item"]
    assert second_dashboard.status_code == 200
    assert body["snapshot_id"] == latest_snapshot.id
    assert body["pace"]["weekly_safe_to_spend_cents"] == latest_snapshot.result_json[
        "outputs"
    ]["weekly_safe_to_spend_cents"]
    assert body["pace"]["current_week_opening_allowance_cents"] == first_opening_allowance
    assert body["pace"]["current_week_remainder_cents"] == first_opening_allowance
    weekly_plans = _weekly_plans(engine)
    assert len(weekly_plans) == 1
    assert weekly_plans[0].id == first_plan.id


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


def _complete_required_setup(
    client: TestClient,
    *,
    email: str = "nati@example.com",
) -> str:
    csrf_token = _register(client, email=email)
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


def _goal_payload() -> dict[str, object]:
    return {
        "name": "Emergency fund",
        "target_cents": 300000,
        "initial_saved_cents": 50000,
        "current_saved_cents": 75000,
        "start_date": "2026-08-01",
        "target_date": "2026-12-31",
    }


def _profile_payload() -> dict[str, object]:
    return {
        "starting_cash_cents": 120000,
        "balance_as_of_date": "2026-08-07",
        "reserve_buffer_cents": 5000,
        "reserve_buffer_confirmed": True,
    }


def _income_payload() -> dict[str, object]:
    return {
        "name": "Campus job",
        "amount_cents": 45000,
        "next_date": "2026-08-14",
        "frequency": "weekly",
        "confidence": "confirmed",
    }


def _snapshot_count(engine: Engine) -> int:
    with Session(engine) as db_session:
        return len(list(db_session.scalars(select(CalculationSnapshot))))


def _latest_snapshot(engine: Engine) -> CalculationSnapshot:
    with Session(engine) as db_session:
        snapshot = db_session.scalar(
            select(CalculationSnapshot).order_by(
                CalculationSnapshot.calculated_at.desc(),
                CalculationSnapshot.id.desc(),
            ),
        )
        assert snapshot is not None
        return snapshot


def _weekly_plans(engine: Engine) -> list[WeeklyPlan]:
    with Session(engine) as db_session:
        return list(db_session.scalars(select(WeeklyPlan).order_by(WeeklyPlan.week_start)))
