from datetime import UTC, date, datetime

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.repositories.auth import create_user
from app.services.goal_inputs import (
    GoalInputValidationError,
    GoalNotFoundError,
    create_goal_for_user,
    get_active_goal_for_user,
    update_goal_for_user,
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


def test_create_goal_for_user_validates_and_persists_active_goal(db_session: Session) -> None:
    user = _create_user(db_session)

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
        now=datetime(2026, 8, 7, 23, 30, tzinfo=UTC),
    )

    assert goal.user_id == user.id
    assert goal.status == "active"
    assert get_active_goal_for_user(db_session, user_id=user.id) == goal


def test_create_goal_rejects_target_date_not_after_user_local_today(
    db_session: Session,
) -> None:
    user = _create_user(db_session)

    with pytest.raises(GoalInputValidationError) as exc_info:
        create_goal_for_user(
            db_session,
            user_id=user.id,
            name="Too soon",
            target_cents=300000,
            initial_saved_cents=0,
            current_saved_cents=0,
            start_date=date(2026, 8, 1),
            target_date=date(2026, 8, 7),
            user_time_zone=user.time_zone,
            now=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        )

    assert exc_info.value.fields == {
        "target_date": ["Must be after the user's current local date."]
    }


def test_create_goal_rejects_invalid_money_fields(db_session: Session) -> None:
    user = _create_user(db_session)

    with pytest.raises(GoalInputValidationError) as exc_info:
        create_goal_for_user(
            db_session,
            user_id=user.id,
            name="Invalid money",
            target_cents=0,
            initial_saved_cents=-1,
            current_saved_cents=200000,
            start_date=date(2026, 8, 1),
            target_date=date(2026, 12, 31),
            user_time_zone=user.time_zone,
            now=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        )

    assert exc_info.value.fields == {
        "target_cents": ["Must be greater than zero."],
        "initial_saved_cents": ["Must be greater than or equal to zero."],
        "current_saved_cents": ["Cannot be greater than target_cents."],
    }


def test_create_goal_rejects_second_active_goal(db_session: Session) -> None:
    user = _create_user(db_session)
    kwargs = {
        "db_session": db_session,
        "user_id": user.id,
        "name": "Emergency fund",
        "target_cents": 300000,
        "initial_saved_cents": 0,
        "current_saved_cents": 0,
        "start_date": date(2026, 8, 1),
        "target_date": date(2026, 12, 31),
        "user_time_zone": user.time_zone,
        "now": datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
    }
    create_goal_for_user(**kwargs)

    with pytest.raises(GoalInputValidationError) as exc_info:
        create_goal_for_user(**kwargs)

    assert exc_info.value.fields == {"goal": ["An active goal already exists."]}


def test_update_goal_for_user_marks_completed_when_current_saved_reaches_target(
    db_session: Session,
) -> None:
    user = _create_user(db_session)
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
        now=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
    )

    updated_goal = update_goal_for_user(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        name="Emergency fund",
        target_cents=300000,
        initial_saved_cents=50000,
        current_saved_cents=300000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        user_time_zone=user.time_zone,
        now=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
    )

    assert updated_goal.status == "completed"
    assert get_active_goal_for_user(db_session, user_id=user.id) is None


def test_update_goal_for_user_returns_not_found_for_cross_user_access(
    db_session: Session,
) -> None:
    owner = _create_user(db_session, email_normalized="owner@example.com")
    other_user = _create_user(db_session, email_normalized="other@example.com")
    goal = create_goal_for_user(
        db_session,
        user_id=owner.id,
        name="Owner goal",
        target_cents=300000,
        initial_saved_cents=50000,
        current_saved_cents=75000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        user_time_zone=owner.time_zone,
        now=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
    )

    with pytest.raises(GoalNotFoundError):
        update_goal_for_user(
            db_session,
            user_id=other_user.id,
            goal_id=goal.id,
            name="Stolen goal",
            target_cents=300000,
            initial_saved_cents=50000,
            current_saved_cents=100000,
            start_date=date(2026, 8, 1),
            target_date=date(2026, 12, 31),
            user_time_zone=other_user.time_zone,
            now=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        )


def _create_user(db_session: Session, *, email_normalized: str = "nati@example.com"):
    return create_user(
        db_session,
        email_normalized=email_normalized,
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
