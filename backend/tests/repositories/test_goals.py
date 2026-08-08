from datetime import date

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.repositories.auth import create_user
from app.repositories.goals import create_goal, get_active_goal, get_goal_for_user, update_goal
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
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


def test_get_active_goal_filters_by_user(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="owner@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    other_user = create_user(
        db_session,
        email_normalized="other@example.com",
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
    create_goal(
        db_session,
        user_id=other_user.id,
        name="Laptop",
        target_cents=150000,
        initial_saved_cents=10000,
        current_saved_cents=25000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 11, 30),
        status="active",
    )
    db_session.commit()

    assert get_active_goal(db_session, user_id=user.id) == goal


def test_completed_goal_is_not_returned_as_active(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="completed@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    create_goal(
        db_session,
        user_id=user.id,
        name="Done",
        target_cents=100000,
        initial_saved_cents=0,
        current_saved_cents=100000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        status="completed",
    )
    db_session.commit()

    assert get_active_goal(db_session, user_id=user.id) is None


def test_get_goal_for_user_returns_none_for_cross_user_access(db_session: Session) -> None:
    owner = create_user(
        db_session,
        email_normalized="goal-owner@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    other_user = create_user(
        db_session,
        email_normalized="goal-other@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    goal = create_goal(
        db_session,
        user_id=owner.id,
        name="Owner goal",
        target_cents=100000,
        initial_saved_cents=0,
        current_saved_cents=10000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        status="active",
    )
    db_session.commit()

    assert get_goal_for_user(db_session, user_id=other_user.id, goal_id=goal.id) is None


def test_update_goal_changes_owned_record(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="update-goal@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    goal = create_goal(
        db_session,
        user_id=user.id,
        name="Old name",
        target_cents=100000,
        initial_saved_cents=0,
        current_saved_cents=10000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        status="active",
    )

    updated_goal = update_goal(
        db_session,
        goal=goal,
        name="New name",
        target_cents=100000,
        initial_saved_cents=0,
        current_saved_cents=25000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        status="active",
    )
    db_session.commit()

    assert updated_goal.name == "New name"
    assert updated_goal.current_saved_cents == 25000


def test_second_active_goal_for_user_hits_database_guard(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="unique-active@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    create_goal(
        db_session,
        user_id=user.id,
        name="First",
        target_cents=100000,
        initial_saved_cents=0,
        current_saved_cents=0,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        status="active",
    )
    db_session.commit()

    with pytest.raises(IntegrityError):
        create_goal(
            db_session,
            user_id=user.id,
            name="Second",
            target_cents=200000,
            initial_saved_cents=0,
            current_saved_cents=0,
            start_date=date(2026, 8, 1),
            target_date=date(2027, 1, 31),
            status="active",
        )
