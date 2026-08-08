from datetime import UTC, date, datetime

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.repositories.auth import create_user
from app.repositories.calculation_snapshots import create_calculation_snapshot
from app.repositories.goals import create_goal
from app.repositories.weekly_plans import create_weekly_plan, get_weekly_plan
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


def test_create_and_get_weekly_plan_filters_by_user(db_session: Session) -> None:
    user, goal, snapshot = _create_user_goal_and_snapshot(
        db_session,
        email_normalized="owner@example.com",
    )
    other_user, other_goal, other_snapshot = _create_user_goal_and_snapshot(
        db_session,
        email_normalized="other@example.com",
    )
    weekly_plan = create_weekly_plan(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        week_start=date(2026, 8, 3),
        opening_allowance_cents=15400,
        created_from_snapshot_id=snapshot.id,
    )
    other_weekly_plan = create_weekly_plan(
        db_session,
        user_id=other_user.id,
        goal_id=other_goal.id,
        week_start=date(2026, 8, 3),
        opening_allowance_cents=99999,
        created_from_snapshot_id=other_snapshot.id,
    )
    db_session.commit()

    assert (
        get_weekly_plan(
            db_session,
            user_id=user.id,
            goal_id=goal.id,
            week_start=date(2026, 8, 3),
        )
        == weekly_plan
    )
    assert (
        get_weekly_plan(
            db_session,
            user_id=user.id,
            goal_id=other_goal.id,
            week_start=date(2026, 8, 3),
        )
        is None
    )
    assert (
        get_weekly_plan(
            db_session,
            user_id=other_user.id,
            goal_id=other_goal.id,
            week_start=date(2026, 8, 3),
        )
        == other_weekly_plan
    )


def _create_user_goal_and_snapshot(
    db_session: Session,
    *,
    email_normalized: str,
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
    snapshot = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="financial_profile_updated",
        normalized_input_json={"schema_version": "snapshot-input-v1"},
        result_json={
            "schema_version": "snapshot-result-v1",
            "outputs": {"weekly_safe_to_spend_cents": 15400},
        },
        calculated_at=datetime(2026, 8, 8, 12, 0, tzinfo=UTC),
    )
    return user, goal, snapshot
