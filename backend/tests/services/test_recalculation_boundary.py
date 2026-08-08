from datetime import UTC, date, datetime

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.repositories.auth import create_user
from app.repositories.financial_inputs import (
    create_income_source,
    create_planned_expense,
    deactivate_income_source,
    deactivate_planned_expense,
)
from app.services.financial_inputs import upsert_financial_profile_for_user
from app.services.goal_inputs import create_goal_for_user
from app.services.recalculation_boundary import (
    MissingInput,
    RecalculationStatus,
    prepare_pace_input_for_user,
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


def test_prepare_pace_input_reports_missing_goal_and_profile(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="missing@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )

    result = prepare_pace_input_for_user(
        db_session,
        user_id=user.id,
        user_time_zone=user.time_zone,
        calculated_at=_now(),
    )

    assert result.status is RecalculationStatus.MISSING_INPUTS
    assert result.missing_inputs == (
        MissingInput.ACTIVE_GOAL,
        MissingInput.FINANCIAL_PROFILE,
    )
    assert result.pace_input is None


def test_prepare_pace_input_requires_confirmed_reserve_buffer(db_session: Session) -> None:
    user = _create_user_with_goal(db_session)
    upsert_financial_profile_for_user(
        db_session,
        user_id=user.id,
        starting_cash_cents=120000,
        balance_as_of_date=date(2026, 8, 7),
        reserve_buffer_cents=5000,
        reserve_buffer_confirmed=False,
        user_time_zone=user.time_zone,
        now=_now(),
    )

    result = prepare_pace_input_for_user(
        db_session,
        user_id=user.id,
        user_time_zone=user.time_zone,
        calculated_at=_now(),
    )

    assert result.status is RecalculationStatus.MISSING_INPUTS
    assert result.missing_inputs == (MissingInput.RESERVE_BUFFER_CONFIRMATION,)
    assert result.pace_input is None


def test_prepare_pace_input_normalizes_complete_user_records(db_session: Session) -> None:
    user = _create_user_with_goal(db_session)
    upsert_financial_profile_for_user(
        db_session,
        user_id=user.id,
        starting_cash_cents=120000,
        balance_as_of_date=date(2026, 8, 7),
        reserve_buffer_cents=5000,
        reserve_buffer_confirmed=True,
        user_time_zone=user.time_zone,
        now=_now(),
    )
    income = create_income_source(
        db_session,
        user_id=user.id,
        name="Campus job",
        amount_cents=45000,
        next_date=date(2026, 8, 14),
        frequency="weekly",
        confidence="confirmed",
    )
    expense = create_planned_expense(
        db_session,
        user_id=user.id,
        name="Rent",
        amount_cents=90000,
        next_date=date(2026, 9, 1),
        frequency="monthly",
        classification="essential",
    )

    result = prepare_pace_input_for_user(
        db_session,
        user_id=user.id,
        user_time_zone=user.time_zone,
        calculated_at=_now(),
    )

    assert result.status is RecalculationStatus.READY
    assert result.missing_inputs == ()
    assert result.pace_input is not None
    assert result.pace_input.user_time_zone == "America/Los_Angeles"
    assert result.pace_input.target_cents == 300000
    assert result.pace_input.starting_cash_cents == 120000
    assert result.pace_input.reserve_buffer_cents == 5000
    assert result.pace_input.income_sources[0].name == income.name
    assert result.pace_input.income_sources[0].frequency.value == "weekly"
    assert result.pace_input.income_sources[0].confidence.value == "confirmed"
    assert result.pace_input.planned_expenses[0].name == expense.name
    assert result.pace_input.planned_expenses[0].classification.value == "essential"


def test_prepare_pace_input_excludes_inactive_income_and_expenses(db_session: Session) -> None:
    user = _create_user_with_goal(db_session)
    upsert_financial_profile_for_user(
        db_session,
        user_id=user.id,
        starting_cash_cents=120000,
        balance_as_of_date=date(2026, 8, 7),
        reserve_buffer_cents=5000,
        reserve_buffer_confirmed=True,
        user_time_zone=user.time_zone,
        now=_now(),
    )
    income = create_income_source(
        db_session,
        user_id=user.id,
        name="Inactive job",
        amount_cents=45000,
        next_date=date(2026, 8, 14),
        frequency="weekly",
        confidence="confirmed",
    )
    expense = create_planned_expense(
        db_session,
        user_id=user.id,
        name="Inactive rent",
        amount_cents=90000,
        next_date=date(2026, 9, 1),
        frequency="monthly",
        classification="essential",
    )
    deactivate_income_source(db_session, income_source=income)
    deactivate_planned_expense(db_session, planned_expense=expense)

    result = prepare_pace_input_for_user(
        db_session,
        user_id=user.id,
        user_time_zone=user.time_zone,
        calculated_at=_now(),
    )

    assert result.status is RecalculationStatus.READY
    assert result.pace_input is not None
    assert result.pace_input.income_sources == ()
    assert result.pace_input.planned_expenses == ()


def _create_user_with_goal(db_session: Session):
    user = create_user(
        db_session,
        email_normalized="nati@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    create_goal_for_user(
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
    return user


def _now() -> datetime:
    return datetime(2026, 8, 7, 12, 0, tzinfo=UTC)
