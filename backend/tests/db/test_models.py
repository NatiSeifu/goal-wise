from datetime import UTC, date, timedelta
from uuid import UUID

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.db.types import utc_now
from app.models import (
    CalculationSnapshot,
    FinancialProfile,
    Goal,
    IncomeSource,
    LoginAttempt,
    PlannedExpense,
    User,
    UserSession,
    WeeklyPlan,
)
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


@pytest.fixture
def engine() -> Engine:
    sqlite_engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(sqlite_engine)
    return sqlite_engine


@pytest.fixture
def session(engine: Engine) -> Session:
    session_factory = make_session_factory(engine)
    with session_factory() as db_session:
        yield db_session


def test_metadata_registers_auth_tables() -> None:
    assert "users" in Base.metadata.tables
    assert "sessions" in Base.metadata.tables
    assert "login_attempts" in Base.metadata.tables
    assert "goals" in Base.metadata.tables
    assert "financial_profiles" in Base.metadata.tables
    assert "income_sources" in Base.metadata.tables
    assert "planned_expenses" in Base.metadata.tables
    assert "calculation_snapshots" in Base.metadata.tables
    assert "weekly_plans" in Base.metadata.tables


def test_user_and_session_round_trip(session: Session) -> None:
    user = User(
        email_normalized="nati@example.com",
        password_hash="argon2-hash-placeholder",
        time_zone="America/Los_Angeles",
    )
    session.add(user)
    session.flush()

    user_session = UserSession(
        user_id=user.id,
        session_token_hash="session-token-hash",
        csrf_token_hash="csrf-token-hash",
        expires_at=utc_now() + timedelta(days=7),
    )
    session.add(user_session)
    session.commit()

    session.refresh(user)
    session.refresh(user_session)

    assert UUID(user.id).version == 4
    assert UUID(user_session.id).version == 4
    assert user_session.user_id == user.id
    assert user_session.user == user
    assert user.created_at.tzinfo is UTC
    assert user_session.expires_at.tzinfo is UTC


def test_user_email_is_unique(session: Session) -> None:
    session.add(
        User(
            email_normalized="same@example.com",
            password_hash="first",
            time_zone="America/Los_Angeles",
        )
    )
    session.commit()

    session.add(
        User(
            email_normalized="same@example.com",
            password_hash="second",
            time_zone="America/Los_Angeles",
        )
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_session_token_hash_is_unique(session: Session) -> None:
    user = User(
        email_normalized="session-owner@example.com",
        password_hash="argon2-hash-placeholder",
        time_zone="America/Los_Angeles",
    )
    session.add(user)
    session.flush()

    expires_at = utc_now() + timedelta(days=7)
    session.add_all(
        [
            UserSession(
                user_id=user.id,
                session_token_hash="same-token-hash",
                csrf_token_hash="csrf-token-hash-1",
                expires_at=expires_at,
            ),
            UserSession(
                user_id=user.id,
                session_token_hash="same-token-hash",
                csrf_token_hash="csrf-token-hash-2",
                expires_at=expires_at,
            ),
        ]
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_session_model_does_not_store_raw_tokens() -> None:
    column_names = set(UserSession.__table__.columns.keys())

    assert "session_token" not in column_names
    assert "csrf_token" not in column_names
    assert "session_token_hash" in column_names
    assert "csrf_token_hash" in column_names


def test_login_attempt_round_trip(session: Session) -> None:
    login_attempt = LoginAttempt(
        email_normalized="nati@example.com",
        source_hash="source-hash",
        failed_at=utc_now(),
    )
    session.add(login_attempt)
    session.commit()
    session.refresh(login_attempt)

    assert login_attempt.id
    assert login_attempt.source_hash == "source-hash"


def test_goal_and_financial_inputs_round_trip(session: Session) -> None:
    user = User(
        email_normalized="planner@example.com",
        password_hash="argon2-hash-placeholder",
        time_zone="America/Los_Angeles",
    )
    session.add(user)
    session.flush()

    goal = Goal(
        user_id=user.id,
        name="Emergency fund",
        target_cents=300000,
        initial_saved_cents=50000,
        current_saved_cents=75000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        status="active",
    )
    profile = FinancialProfile(
        user_id=user.id,
        starting_cash_cents=120000,
        balance_as_of_date=date(2026, 8, 1),
        reserve_buffer_cents=5000,
        reserve_buffer_confirmed=True,
    )
    income = IncomeSource(
        user_id=user.id,
        name="Campus job",
        amount_cents=45000,
        next_date=date(2026, 8, 7),
        frequency="weekly",
        confidence="confirmed",
        active=True,
    )
    expense = PlannedExpense(
        user_id=user.id,
        name="Rent",
        amount_cents=90000,
        next_date=date(2026, 9, 1),
        frequency="monthly",
        classification="essential",
        active=True,
    )

    session.add_all([goal, profile, income, expense])
    session.commit()

    session.refresh(goal)
    session.refresh(profile)
    session.refresh(income)
    session.refresh(expense)

    assert UUID(goal.id).version == 4
    assert UUID(profile.id).version == 4
    assert UUID(income.id).version == 4
    assert UUID(expense.id).version == 4
    assert goal.user_id == user.id
    assert profile.user_id == user.id
    assert income.user_id == user.id
    assert expense.user_id == user.id
    assert goal.created_at.tzinfo is UTC
    assert profile.updated_at.tzinfo is UTC


def test_user_has_at_most_one_active_goal(session: Session) -> None:
    user = User(
        email_normalized="active-goal@example.com",
        password_hash="argon2-hash-placeholder",
        time_zone="America/Los_Angeles",
    )
    session.add(user)
    session.flush()

    session.add(
        Goal(
            user_id=user.id,
            name="First active goal",
            target_cents=100000,
            initial_saved_cents=0,
            current_saved_cents=0,
            start_date=date(2026, 8, 1),
            target_date=date(2026, 12, 31),
            status="active",
        )
    )
    session.commit()

    session.add(
        Goal(
            user_id=user.id,
            name="Second active goal",
            target_cents=200000,
            initial_saved_cents=0,
            current_saved_cents=0,
            start_date=date(2026, 8, 1),
            target_date=date(2027, 1, 31),
            status="active",
        )
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_calculation_snapshot_round_trip(session: Session) -> None:
    user = User(
        email_normalized="snapshot@example.com",
        password_hash="argon2-hash-placeholder",
        time_zone="America/Los_Angeles",
    )
    session.add(user)
    session.flush()
    goal = Goal(
        user_id=user.id,
        name="Emergency fund",
        target_cents=300000,
        initial_saved_cents=50000,
        current_saved_cents=75000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        status="active",
    )
    session.add(goal)
    session.flush()

    calculated_at = utc_now()
    snapshot = CalculationSnapshot(
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="goal_updated",
        normalized_input_json={
            "schema_version": "snapshot-input-v1",
            "formula_version": "pace-v1",
        },
        result_json={
            "schema_version": "snapshot-result-v1",
            "formula_version": "pace-v1",
        },
        calculated_at=calculated_at,
    )
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)

    assert UUID(snapshot.id).version == 4
    assert snapshot.user_id == user.id
    assert snapshot.goal_id == goal.id
    assert snapshot.user == user
    assert snapshot.goal == goal
    assert snapshot.normalized_input_json["schema_version"] == "snapshot-input-v1"
    assert snapshot.result_json["schema_version"] == "snapshot-result-v1"
    assert snapshot.calculated_at.tzinfo is UTC
    assert snapshot.created_at.tzinfo is UTC


def test_weekly_plan_round_trip_and_uniqueness(session: Session) -> None:
    user = User(
        email_normalized="weekly-plan@example.com",
        password_hash="argon2-hash-placeholder",
        time_zone="America/Los_Angeles",
    )
    session.add(user)
    session.flush()
    goal = Goal(
        user_id=user.id,
        name="Emergency fund",
        target_cents=300000,
        initial_saved_cents=50000,
        current_saved_cents=75000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        status="active",
    )
    session.add(goal)
    session.flush()
    snapshot = CalculationSnapshot(
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="financial_profile_updated",
        normalized_input_json={"schema_version": "snapshot-input-v1"},
        result_json={
            "schema_version": "snapshot-result-v1",
            "outputs": {"weekly_safe_to_spend_cents": 15400},
        },
        calculated_at=utc_now(),
    )
    session.add(snapshot)
    session.flush()
    weekly_plan = WeeklyPlan(
        user_id=user.id,
        goal_id=goal.id,
        week_start=date(2026, 8, 3),
        opening_allowance_cents=15400,
        created_from_snapshot_id=snapshot.id,
    )
    session.add(weekly_plan)
    session.commit()
    session.refresh(weekly_plan)

    assert UUID(weekly_plan.id).version == 4
    assert weekly_plan.user_id == user.id
    assert weekly_plan.goal_id == goal.id
    assert weekly_plan.snapshot == snapshot
    assert weekly_plan.created_at.tzinfo is UTC

    session.add(
        WeeklyPlan(
            user_id=user.id,
            goal_id=goal.id,
            week_start=date(2026, 8, 3),
            opening_allowance_cents=99999,
            created_from_snapshot_id=snapshot.id,
        )
    )

    with pytest.raises(IntegrityError):
        session.commit()


def test_calculation_snapshot_model_is_insert_only_shape() -> None:
    column_names = set(CalculationSnapshot.__table__.columns.keys())

    assert "created_at" in column_names
    assert "updated_at" not in column_names
