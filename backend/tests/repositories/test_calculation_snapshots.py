from datetime import UTC, date, datetime, timedelta

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.repositories.auth import create_user
from app.repositories.calculation_snapshots import (
    create_calculation_snapshot,
    get_latest_snapshot_for_user,
    get_latest_snapshot_for_user_and_goal,
    get_previous_snapshot_for_user,
    list_snapshots_for_user,
)
from app.repositories.goals import create_goal, update_goal
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


def test_create_calculation_snapshot_persists_json_payloads(db_session: Session) -> None:
    user, goal = _create_user_and_goal(db_session)
    calculated_at = _calculated_at()

    snapshot = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="goal_updated",
        normalized_input_json=_input_json(goal_id=goal.id),
        result_json=_result_json(weekly_safe_to_spend_cents=15000),
        calculated_at=calculated_at,
    )
    db_session.commit()

    assert snapshot.id
    assert snapshot.user_id == user.id
    assert snapshot.goal_id == goal.id
    assert snapshot.formula_version == "pace-v1"
    assert snapshot.trigger == "goal_updated"
    assert snapshot.normalized_input_json["goal"]["id"] == goal.id
    assert snapshot.result_json["outputs"]["weekly_safe_to_spend_cents"] == 15000
    assert snapshot.calculated_at == calculated_at


def test_get_latest_snapshot_for_user_filters_by_owner_and_uses_deterministic_order(
    db_session: Session,
) -> None:
    user, goal = _create_user_and_goal(db_session, email_normalized="owner@example.com")
    other_user, other_goal = _create_user_and_goal(
        db_session,
        email_normalized="other@example.com",
    )
    first = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="goal_updated",
        normalized_input_json=_input_json(goal_id=goal.id),
        result_json=_result_json(weekly_safe_to_spend_cents=10000),
        calculated_at=_calculated_at(),
    )
    second_same_time = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="income_source_updated",
        normalized_input_json=_input_json(goal_id=goal.id),
        result_json=_result_json(weekly_safe_to_spend_cents=12000),
        calculated_at=_calculated_at() + timedelta(minutes=1),
    )
    third_same_time = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="planned_expense_updated",
        normalized_input_json=_input_json(goal_id=goal.id),
        result_json=_result_json(weekly_safe_to_spend_cents=13000),
        calculated_at=_calculated_at() + timedelta(minutes=1),
    )
    create_calculation_snapshot(
        db_session,
        user_id=other_user.id,
        goal_id=other_goal.id,
        formula_version="pace-v1",
        trigger="goal_updated",
        normalized_input_json=_input_json(goal_id=other_goal.id),
        result_json=_result_json(weekly_safe_to_spend_cents=99999),
        calculated_at=_calculated_at() + timedelta(days=1),
    )
    db_session.commit()

    assert get_latest_snapshot_for_user(db_session, user_id=user.id) == third_same_time
    assert get_latest_snapshot_for_user(db_session, user_id=other_user.id).goal_id == other_goal.id
    assert list_snapshots_for_user(db_session, user_id=user.id, limit=10) == [
        third_same_time,
        second_same_time,
        first,
    ]


def test_get_latest_snapshot_for_user_and_goal_filters_by_goal(db_session: Session) -> None:
    user, first_goal = _create_user_and_goal(db_session)
    second_goal = create_goal(
        db_session,
        user_id=user.id,
        name="Laptop",
        target_cents=150000,
        initial_saved_cents=0,
        current_saved_cents=10000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 11, 30),
        status="archived",
    )
    first_snapshot = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=first_goal.id,
        formula_version="pace-v1",
        trigger="goal_updated",
        normalized_input_json=_input_json(goal_id=first_goal.id),
        result_json=_result_json(weekly_safe_to_spend_cents=10000),
        calculated_at=_calculated_at(),
    )
    second_snapshot = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=second_goal.id,
        formula_version="pace-v1",
        trigger="goal_updated",
        normalized_input_json=_input_json(goal_id=second_goal.id),
        result_json=_result_json(weekly_safe_to_spend_cents=20000),
        calculated_at=_calculated_at() + timedelta(hours=1),
    )
    db_session.commit()

    assert (
        get_latest_snapshot_for_user_and_goal(
            db_session,
            user_id=user.id,
            goal_id=first_goal.id,
        )
        == first_snapshot
    )
    assert (
        get_latest_snapshot_for_user_and_goal(
            db_session,
            user_id=user.id,
            goal_id=second_goal.id,
        )
        == second_snapshot
    )


def test_get_previous_snapshot_for_user_filters_by_owner(db_session: Session) -> None:
    user, goal = _create_user_and_goal(db_session, email_normalized="owner@example.com")
    other_user, other_goal = _create_user_and_goal(
        db_session,
        email_normalized="other@example.com",
    )
    first = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="goal_updated",
        normalized_input_json=_input_json(goal_id=goal.id),
        result_json=_result_json(weekly_safe_to_spend_cents=10000),
        calculated_at=_calculated_at(),
    )
    second = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="income_source_updated",
        normalized_input_json=_input_json(goal_id=goal.id),
        result_json=_result_json(weekly_safe_to_spend_cents=12000),
        calculated_at=_calculated_at() + timedelta(hours=1),
    )
    create_calculation_snapshot(
        db_session,
        user_id=other_user.id,
        goal_id=other_goal.id,
        formula_version="pace-v1",
        trigger="goal_updated",
        normalized_input_json=_input_json(goal_id=other_goal.id),
        result_json=_result_json(weekly_safe_to_spend_cents=99999),
        calculated_at=_calculated_at() + timedelta(minutes=30),
    )
    db_session.commit()

    assert get_previous_snapshot_for_user(db_session, user_id=user.id, snapshot=second) == first
    assert (
        get_previous_snapshot_for_user(
            db_session,
            user_id=other_user.id,
            snapshot=second,
        )
        is None
    )


def test_snapshot_json_is_unchanged_when_source_goal_changes(db_session: Session) -> None:
    user, goal = _create_user_and_goal(db_session)
    snapshot = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="goal_updated",
        normalized_input_json=_input_json(goal_id=goal.id, goal_name=goal.name),
        result_json=_result_json(weekly_safe_to_spend_cents=15000),
        calculated_at=_calculated_at(),
    )
    db_session.commit()

    update_goal(
        db_session,
        goal=goal,
        name="Renamed goal",
        target_cents=goal.target_cents,
        initial_saved_cents=goal.initial_saved_cents,
        current_saved_cents=goal.current_saved_cents,
        start_date=goal.start_date,
        target_date=goal.target_date,
        status=goal.status,
    )
    db_session.commit()

    assert snapshot.normalized_input_json["goal"]["name"] == "Emergency fund"
    assert goal.name == "Renamed goal"


def _create_user_and_goal(
    db_session: Session,
    *,
    email_normalized: str = "nati@example.com",
):
    user = create_user(
        db_session,
        email_normalized=email_normalized,
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
    return user, goal


def _calculated_at() -> datetime:
    return datetime(2026, 8, 8, 12, 0, tzinfo=UTC)


def _input_json(*, goal_id: str, goal_name: str = "Emergency fund") -> dict[str, object]:
    return {
        "schema_version": "snapshot-input-v1",
        "formula_version": "pace-v1",
        "calculation": {
            "timestamp_utc": "2026-08-08T12:00:00Z",
            "user_time_zone": "America/Los_Angeles",
            "trigger": "goal_updated",
        },
        "goal": {
            "id": goal_id,
            "name": goal_name,
        },
        "financial_profile": {},
        "income_sources": [],
        "planned_expenses": [],
        "transactions": [],
    }


def _result_json(*, weekly_safe_to_spend_cents: int) -> dict[str, object]:
    return {
        "schema_version": "snapshot-result-v1",
        "formula_version": "pace-v1",
        "outputs": {
            "weekly_safe_to_spend_cents": weekly_safe_to_spend_cents,
        },
        "explanation": {},
        "changed_from_previous": {},
    }
