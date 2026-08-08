from datetime import UTC, date, datetime

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.repositories.auth import create_user
from app.repositories.calculation_snapshots import list_snapshots_for_user
from app.repositories.financial_inputs import create_income_source, create_planned_expense
from app.services.financial_inputs import upsert_financial_profile_for_user
from app.services.goal_inputs import create_goal_for_user, update_goal_for_user
from app.services.snapshot_calculation import (
    SnapshotCalculationStatus,
    calculate_and_snapshot_for_user,
)
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


def test_calculate_and_snapshot_returns_missing_inputs_without_insert(
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        email_normalized="missing@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )

    result = calculate_and_snapshot_for_user(
        db_session,
        user_id=user.id,
        user_time_zone=user.time_zone,
        trigger="dashboard_opened",
        calculated_at=_now(),
    )

    assert result.status is SnapshotCalculationStatus.MISSING_INPUTS
    assert tuple(reason.value for reason in result.missing_inputs) == (
        "active_goal",
        "financial_profile",
    )
    assert result.snapshot is None
    assert list_snapshots_for_user(db_session, user_id=user.id, limit=10) == []


def test_calculate_and_snapshot_blocks_unconfirmed_reserve_buffer(
    db_session: Session,
) -> None:
    user, _goal_id = _create_ready_user(db_session, reserve_buffer_confirmed=False)

    result = calculate_and_snapshot_for_user(
        db_session,
        user_id=user.id,
        user_time_zone=user.time_zone,
        trigger="financial_profile_updated",
        calculated_at=_now(),
    )

    assert result.status is SnapshotCalculationStatus.MISSING_INPUTS
    assert tuple(reason.value for reason in result.missing_inputs) == (
        "reserve_buffer_confirmation",
    )
    assert result.snapshot is None
    assert list_snapshots_for_user(db_session, user_id=user.id, limit=10) == []


def test_calculate_and_snapshot_creates_immutable_snapshot_for_complete_inputs(
    db_session: Session,
) -> None:
    user, goal_id = _create_ready_user(db_session)

    result = calculate_and_snapshot_for_user(
        db_session,
        user_id=user.id,
        user_time_zone=user.time_zone,
        trigger="income_source_created",
        calculated_at=_now(),
    )

    assert result.status is SnapshotCalculationStatus.CREATED
    assert result.snapshot is not None
    assert result.snapshot.user_id == user.id
    assert result.snapshot.goal_id == goal_id
    assert result.snapshot.formula_version == "pace-v1"
    assert result.snapshot.trigger == "income_source_created"
    assert result.snapshot.normalized_input_json["schema_version"] == "snapshot-input-v1"
    assert result.snapshot.result_json["schema_version"] == "snapshot-result-v1"
    assert result.snapshot.result_json["outputs"]["weekly_safe_to_spend_cents"] == 20400
    assert len(list_snapshots_for_user(db_session, user_id=user.id, limit=10)) == 1


def test_calculate_and_snapshot_compares_against_previous_snapshot(
    db_session: Session,
) -> None:
    user, goal_id = _create_ready_user(db_session)
    first = calculate_and_snapshot_for_user(
        db_session,
        user_id=user.id,
        user_time_zone=user.time_zone,
        trigger="dashboard_opened",
        calculated_at=_now(),
    )
    assert first.snapshot is not None
    goal = first.snapshot.goal
    update_goal_for_user(
        db_session,
        user_id=user.id,
        goal_id=goal_id,
        name="Emergency fund",
        target_cents=300000,
        initial_saved_cents=50000,
        current_saved_cents=125000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        user_time_zone=user.time_zone,
        now=_now(),
    )

    second = calculate_and_snapshot_for_user(
        db_session,
        user_id=user.id,
        user_time_zone=user.time_zone,
        trigger="goal_updated",
        calculated_at=_now().replace(hour=13),
    )

    assert second.snapshot is not None
    changed_from_previous = second.snapshot.result_json["changed_from_previous"]
    assert changed_from_previous["previous_snapshot_id"] == first.snapshot.id
    assert changed_from_previous["changed_input_categories"] == ["goal"]
    assert changed_from_previous["weekly_safe_to_spend_delta_cents"] == 2400
    assert goal.current_saved_cents == 125000


def _create_ready_user(
    db_session: Session,
    *,
    reserve_buffer_confirmed: bool = True,
):
    user = create_user(
        db_session,
        email_normalized="nati@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    goal = create_goal_for_user(
        db_session,
        user_id=user.id,
        name="Emergency fund",
        target_cents=300000,
        initial_saved_cents=50000,
        current_saved_cents=75000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        user_time_zone=user.time_zone,
        now=_now(),
    )
    upsert_financial_profile_for_user(
        db_session,
        user_id=user.id,
        starting_cash_cents=120000,
        balance_as_of_date=date(2026, 8, 7),
        reserve_buffer_cents=5000,
        reserve_buffer_confirmed=reserve_buffer_confirmed,
        user_time_zone=user.time_zone,
        now=_now(),
    )
    create_income_source(
        db_session,
        user_id=user.id,
        name="Campus job",
        amount_cents=45000,
        next_date=date(2026, 8, 14),
        frequency="weekly",
        confidence="confirmed",
    )
    create_planned_expense(
        db_session,
        user_id=user.id,
        name="Rent",
        amount_cents=90000,
        next_date=date(2026, 9, 1),
        frequency="monthly",
        classification="essential",
    )
    return user, goal.id


def _now() -> datetime:
    return datetime(2026, 8, 8, 12, 0, tzinfo=UTC)
