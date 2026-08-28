from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from app.api.constants import SESSION_COOKIE_NAME
from app.api.dependencies import utc_now
from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import get_db_session, make_engine, make_session_factory
from app.main import app
from app.models import CalculationSnapshot, FinancialProfile, Goal, IncomeSource, PlannedExpense
from fastapi.testclient import TestClient
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

TEST_SESSION_SECRET = "test-session-secret"
CSV_HEADER = (
    "record_type,name,target_amount,initial_saved,current_saved,starting_cash,"
    "balance_date,reserve_buffer,amount,date,frequency,confidence,classification,"
    "start_date,target_date"
)
CSV_PLAN = "\n".join(
    [
        CSV_HEADER,
        "goal,Moving fund,3000.00,500.00,1125.00,,,,,,,,,2026-08-01,2026-11-15",
        "cash,,,,,2000.00,2026-08-26,300.00,,,,,,,",
        "income,Salary,,,,,,,2500.00,2026-09-01,biweekly,confirmed,,,",
        "expense,Rent,,,,,,,1400.00,2026-09-01,monthly,,essential,,",
    ]
)


@pytest.fixture
def client_and_engine() -> Generator[tuple[TestClient, Engine], None, None]:
    engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = make_session_factory(engine)

    def override_db_session() -> Generator[Session, None, None]:
        with session_factory() as db_session:
            yield db_session

    def override_settings() -> Settings:
        return Settings(environment="test", session_secret=TEST_SESSION_SECRET)

    def override_utc_now() -> datetime:
        return datetime(2026, 8, 27, 12, 0, tzinfo=UTC)

    app.dependency_overrides[get_db_session] = override_db_session
    app.dependency_overrides[get_settings] = override_settings
    app.dependency_overrides[utc_now] = override_utc_now
    with TestClient(app) as client:
        yield client, engine
    app.dependency_overrides.clear()


def test_preview_requires_csrf(client_and_engine: tuple[TestClient, Engine]) -> None:
    client, _engine = client_and_engine
    _register(client)

    response = client.post(
        "/api/v1/planning-import/preview",
        files={"file": ("plan.csv", CSV_PLAN, "text/csv")},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_failed"


def test_preview_returns_normalized_plan_without_writes(
    client_and_engine: tuple[TestClient, Engine],
) -> None:
    client, engine = client_and_engine
    csrf_token = _register(client)

    response = client.post(
        "/api/v1/planning-import/preview",
        files={"file": ("plan.csv", CSV_PLAN, "text/csv")},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["row_count"] == 4
    assert body["counts"] == {"goal": 1, "cash": 1, "income": 1, "expense": 1}
    assert body["goal"]["target_cents"] == 300000
    assert body["cash"]["starting_cash_cents"] == 200000
    assert body["income_sources"][0]["amount_cents"] == 250000
    assert body["planned_expenses"][0]["classification"] == "essential"
    assert body["errors"] == []

    with Session(engine) as db_session:
        assert db_session.scalar(select(Goal)) is None
        assert db_session.scalar(select(FinancialProfile)) is None
        assert db_session.scalar(select(IncomeSource)) is None
        assert db_session.scalar(select(PlannedExpense)) is None
        assert db_session.scalar(select(CalculationSnapshot)) is None


def test_preview_returns_structured_validation_issues(
    client_and_engine: tuple[TestClient, Engine],
) -> None:
    client, _engine = client_and_engine
    csrf_token = _register(client)
    invalid_csv = "\n".join(
        [
            CSV_HEADER,
            "goal,Goal,10.00,-1,20,,,,,,,,,2026-08-28,2026-08-27",
            "cash,,,,,100.00,2026-08-28,5.00,,,,,,,",
        ]
    )

    response = client.post(
        "/api/v1/planning-import/preview",
        files={"file": ("invalid.csv", invalid_csv, "text/csv")},
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "planning_import_invalid"
    assert {(issue["row"], issue["code"]) for issue in error["issues"]} == {
        (2, "invalid_money"),
        (2, "exceeds_target"),
        (2, "invalid_date_range"),
        (2, "target_date_not_future"),
        (3, "balance_date_in_future"),
    }


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
