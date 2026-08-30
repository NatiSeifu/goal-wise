from datetime import UTC, date, datetime

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.repositories.auth import create_user
from app.repositories.calculation_snapshots import create_calculation_snapshot
from app.repositories.goals import create_goal
from app.services.weekly_plans import get_or_create_current_week_plan
from sqlalchemy import Engine
from sqlalchemy.orm import Session


@pytest.fixture
def engine() -> Engine:
    sqlite_engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(sqlite_engine)
    return sqlite_engine


@pytest.fixture
def db_session(engine: Engine) -> Session:
    session_factory = make_session_factory(engine)
    with session_factory() as session:
        yield session


def test_get_or_create_current_week_plan_uses_user_local_monday(
    db_session: Session,
) -> None:
    user, goal, snapshot = _create_user_goal_and_snapshot(
        db_session,
        weekly_safe_to_spend_cents=15400,
    )

    weekly_plan = get_or_create_current_week_plan(
        db_session,
        user_id=user.id,
        user_time_zone="America/Los_Angeles",
        snapshot=snapshot,
        now=datetime(2026, 8, 8, 12, 0, tzinfo=UTC),
    )

    assert weekly_plan.user_id == user.id
    assert weekly_plan.goal_id == goal.id
    assert weekly_plan.week_start == date(2026, 8, 3)
    assert weekly_plan.opening_allowance_cents == 15400
    assert weekly_plan.created_from_snapshot_id == snapshot.id


def test_get_or_create_current_week_plan_does_not_replace_existing_plan(
    db_session: Session,
) -> None:
    user, _goal, first_snapshot = _create_user_goal_and_snapshot(
        db_session,
        weekly_safe_to_spend_cents=15400,
    )
    first_plan = get_or_create_current_week_plan(
        db_session,
        user_id=user.id,
        user_time_zone="America/Los_Angeles",
        snapshot=first_snapshot,
        now=datetime(2026, 8, 8, 12, 0, tzinfo=UTC),
    )
    second_snapshot = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=first_snapshot.goal_id,
        formula_version="pace-v1",
        trigger="income_source_updated",
        normalized_input_json=_input_json(),
        result_json=_result_json(weekly_safe_to_spend_cents=22200),
        calculated_at=datetime(2026, 8, 9, 12, 0, tzinfo=UTC),
    )

    second_plan = get_or_create_current_week_plan(
        db_session,
        user_id=user.id,
        user_time_zone="America/Los_Angeles",
        snapshot=second_snapshot,
        now=datetime(2026, 8, 9, 12, 0, tzinfo=UTC),
    )

    assert second_plan == first_plan
    assert second_plan.opening_allowance_cents == 15400
    assert second_plan.created_from_snapshot_id == first_snapshot.id


def _create_user_goal_and_snapshot(
    db_session: Session,
    *,
    weekly_safe_to_spend_cents: int,
):
    user = create_user(
        db_session,
        email_normalized="nati@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    goal = create_goal(
        db_session,
        user_id=user.id,
        name="Emergency fund",
        target_cents=300000,
        initial_saved_cents=50000,
        current_saved_cents=75000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        status="active",
    )
    snapshot = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="financial_profile_updated",
        normalized_input_json=_input_json(),
        result_json=_result_json(weekly_safe_to_spend_cents=weekly_safe_to_spend_cents),
        calculated_at=datetime(2026, 8, 8, 12, 0, tzinfo=UTC),
    )
    return user, goal, snapshot


def _input_json() -> dict[str, object]:
    return {
        "schema_version": "snapshot-input-v1",
        "formula_version": "pace-v1",
        "calculation": {
            "timestamp_utc": "2026-08-08T12:00:00Z",
            "user_time_zone": "America/Los_Angeles",
            "trigger": "financial_profile_updated",
        },
        "goal": {
            "id": "goal-1",
            "name": "Emergency fund",
            "target_cents": 300000,
            "initial_saved_cents": 50000,
            "current_saved_cents": 75000,
            "start_date": "2026-08-01",
            "target_date": "2026-12-31",
            "status": "active",
        },
        "financial_profile": {
            "starting_cash_cents": 120000,
            "balance_as_of_date": "2026-08-07",
            "reserve_buffer_cents": 10000,
            "reserve_buffer_confirmed": True,
        },
        "income_sources": [],
        "planned_expenses": [],
        "transactions": [],
    }


def _result_json(*, weekly_safe_to_spend_cents: int) -> dict[str, object]:
    return {
        "schema_version": "snapshot-result-v1",
        "formula_version": "pace-v1",
        "outputs": {
            "current_cash_cents": 120000,
            "confirmed_future_income_cents": 0,
            "planned_future_expenses_cents": 0,
            "reserve_buffer_cents": 10000,
            "forecast_resources_cents": 110000,
            "goal_gap_cents": 225000,
            "discretionary_capacity_cents": weekly_safe_to_spend_cents,
            "remaining_weeks": 20,
            "weekly_safe_to_spend_cents": weekly_safe_to_spend_cents,
            "projected_shortfall_cents": 0,
            "expected_savings_to_date_cents": 75000,
            "pace_status": "On Track",
            "progress_percentage": 25.0,
            "current_week_opening_allowance_cents": weekly_safe_to_spend_cents,
            "current_week_remainder_cents": weekly_safe_to_spend_cents,
        },
        "explanation": {
            "included_income_source_ids": [],
            "excluded_income_source_ids": [],
            "included_planned_expense_ids": [],
            "excluded_planned_expense_ids": [],
            "summary": {
                "confirmed_income_count": 0,
                "planned_expense_count": 0,
                "unconfirmed_income_count": 0,
            },
        },
        "changed_from_previous": {
            "previous_snapshot_id": None,
            "changed_input_categories": [],
            "weekly_safe_to_spend_delta_cents": None,
        },
    }
