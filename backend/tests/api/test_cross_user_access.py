from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from app.api.dependencies import utc_now
from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db_session, make_engine, make_session_factory
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session

TEST_SESSION_SECRET = "test-session-secret"
CSV_PLAN = "\n".join(
    [
        "record_type,name,target_amount,initial_saved,current_saved,starting_cash,balance_date,reserve_buffer,amount,date,frequency,confidence,classification,start_date,target_date",
        "goal,Other fund,3000.00,500.00,1125.00,,,,,,,,,2026-08-01,2026-11-15",
        "cash,,,,,2000.00,2026-08-26,300.00,,,,,,,",
        "income,Other salary,,,,,,,2500.00,2026-09-01,biweekly,confirmed,,,",
        "expense,Other rent,,,,,,,1400.00,2026-09-01,monthly,,essential,,",
    ]
)


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
    app.dependency_overrides[utc_now] = lambda: datetime(2026, 8, 27, 12, 0, tzinfo=UTC)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def engine() -> Engine:
    sqlite_engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(sqlite_engine)
    return sqlite_engine


def test_user_cannot_read_or_mutate_another_users_private_resources(
    client: TestClient,
) -> None:
    owner_csrf, owner_ids = _create_complete_owner_setup(client)
    client.cookies.clear()
    other_csrf = _register(client, email="other@example.com")

    assert client.get("/api/v1/goals/active").json() == {"item": None}
    assert client.get("/api/v1/financial-profile").json() == {"item": None}
    assert client.get("/api/v1/income-sources").json() == {"items": []}
    assert client.get("/api/v1/planned-expenses").json() == {"items": []}
    assert client.get("/api/v1/calculation-snapshots/latest").json() == {"item": None}

    dashboard = client.get("/api/v1/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["item"]["status"] == "setup_required"
    assert dashboard.json()["item"]["snapshot_id"] is None

    csrf_headers = {"X-CSRF-Token": other_csrf}
    for response in (
        client.patch(
            f"/api/v1/goals/{owner_ids['goal_id']}",
            json=_goal_payload(),
            headers=csrf_headers,
        ),
        client.post(
            f"/api/v1/goals/{owner_ids['goal_id']}/archive",
            headers=csrf_headers,
        ),
        client.patch(
            f"/api/v1/income-sources/{owner_ids['income_id']}",
            json=_income_payload(),
            headers=csrf_headers,
        ),
        client.delete(
            f"/api/v1/income-sources/{owner_ids['income_id']}",
            headers=csrf_headers,
        ),
        client.patch(
            f"/api/v1/planned-expenses/{owner_ids['expense_id']}",
            json=_expense_payload(),
            headers=csrf_headers,
        ),
        client.delete(
            f"/api/v1/planned-expenses/{owner_ids['expense_id']}",
            headers=csrf_headers,
        ),
    ):
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    # The owner token is deliberately unused after switching sessions; this
    # assertion documents that a preview is bound to its creating user.
    preview = _preview_import_as_owner(client, owner_csrf)
    client.cookies.clear()
    other_csrf = _login(client, email="other@example.com")
    confirm = client.post(
        "/api/v1/planning-import/confirm",
        json={"preview_token": preview},
        headers={"X-CSRF-Token": other_csrf},
    )
    assert confirm.status_code == 422
    assert confirm.json()["error"]["issues"][0]["code"] == "invalid_preview"


def test_user_cannot_request_another_users_ai_explanation(
    client: TestClient,
) -> None:
    _create_complete_owner_setup(client)
    client.cookies.clear()
    _register(client, email="ai-other@example.com")

    response = client.post(
        "/api/v1/ai-explanations/latest",
        headers={"X-CSRF-Token": _csrf_from_current_session(client)},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "calculation_snapshot_not_found"


def _create_complete_owner_setup(client: TestClient) -> tuple[str, dict[str, int]]:
    csrf_token = _register(client, email="owner@example.com")
    goal = client.post(
        "/api/v1/goals",
        json=_goal_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    assert goal.status_code == 201
    profile = client.put(
        "/api/v1/financial-profile",
        json=_profile_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    assert profile.status_code == 200
    income = client.post(
        "/api/v1/income-sources",
        json=_income_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    assert income.status_code == 201
    expense = client.post(
        "/api/v1/planned-expenses",
        json=_expense_payload(),
        headers={"X-CSRF-Token": csrf_token},
    )
    assert expense.status_code == 201
    return csrf_token, {
        "goal_id": goal.json()["item"]["id"],
        "income_id": income.json()["item"]["id"],
        "expense_id": expense.json()["item"]["id"],
    }


def _preview_import_as_owner(client: TestClient, csrf_token: str) -> str:
    client.cookies.clear()
    _login(client, email="owner@example.com")
    response = client.post(
        "/api/v1/planning-import/preview",
        files={"file": ("plan.csv", CSV_PLAN, "text/csv")},
        headers={"X-CSRF-Token": _csrf_from_current_session(client)},
    )
    assert response.status_code == 200
    return response.json()["preview_token"]


def _register(client: TestClient, *, email: str) -> str:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "correct horse battery staple",
            "time_zone": "America/Los_Angeles",
        },
    )
    assert response.status_code == 201
    return str(response.json()["item"]["csrf_token"])


def _login(client: TestClient, *, email: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "correct horse battery staple"},
    )
    assert response.status_code == 200
    return str(response.json()["item"]["csrf_token"])


def _csrf_from_current_session(client: TestClient) -> str:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
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


def _expense_payload() -> dict[str, object]:
    return {
        "name": "Rent",
        "amount_cents": 90000,
        "next_date": "2026-09-01",
        "frequency": "monthly",
        "classification": "essential",
    }
