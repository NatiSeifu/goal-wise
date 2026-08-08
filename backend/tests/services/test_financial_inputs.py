from datetime import UTC, date, datetime

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.models import User
from app.repositories.auth import create_user
from app.services.financial_inputs import (
    FinancialInputNotFoundError,
    FinancialInputValidationError,
    create_income_source_for_user,
    create_planned_expense_for_user,
    deactivate_income_source_for_user,
    deactivate_planned_expense_for_user,
    upsert_financial_profile_for_user,
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


def test_upsert_financial_profile_validates_and_persists(db_session: Session) -> None:
    user = _create_user(db_session)

    profile = upsert_financial_profile_for_user(
        db_session,
        user_id=user.id,
        starting_cash_cents=120000,
        balance_as_of_date=date(2026, 8, 7),
        reserve_buffer_cents=5000,
        reserve_buffer_confirmed=True,
        user_time_zone=user.time_zone,
        now=datetime(2026, 8, 7, 23, 30, tzinfo=UTC),
    )

    assert profile.user_id == user.id
    assert profile.reserve_buffer_confirmed is True


def test_upsert_financial_profile_rejects_future_balance_date(
    db_session: Session,
) -> None:
    user = _create_user(db_session)

    with pytest.raises(FinancialInputValidationError) as exc_info:
        upsert_financial_profile_for_user(
            db_session,
            user_id=user.id,
            starting_cash_cents=120000,
            balance_as_of_date=date(2026, 8, 8),
            reserve_buffer_cents=5000,
            reserve_buffer_confirmed=True,
            user_time_zone=user.time_zone,
            now=datetime(2026, 8, 7, 23, 30, tzinfo=UTC),
        )

    assert exc_info.value.fields == {
        "balance_as_of_date": ["Cannot be after the user's current local date."]
    }


def test_upsert_financial_profile_rejects_negative_money(db_session: Session) -> None:
    user = _create_user(db_session)

    with pytest.raises(FinancialInputValidationError) as exc_info:
        upsert_financial_profile_for_user(
            db_session,
            user_id=user.id,
            starting_cash_cents=-1,
            balance_as_of_date=date(2026, 8, 7),
            reserve_buffer_cents=-1,
            reserve_buffer_confirmed=False,
            user_time_zone=user.time_zone,
            now=datetime(2026, 8, 7, 23, 30, tzinfo=UTC),
        )

    assert exc_info.value.fields == {
        "starting_cash_cents": ["Must be greater than or equal to zero."],
        "reserve_buffer_cents": ["Must be greater than or equal to zero."],
    }


def test_create_income_source_rejects_invalid_frequency_and_confidence(
    db_session: Session,
) -> None:
    user = _create_user(db_session)

    with pytest.raises(FinancialInputValidationError) as exc_info:
        create_income_source_for_user(
            db_session,
            user_id=user.id,
            name="Campus job",
            amount_cents=0,
            next_date=date(2026, 8, 7),
            frequency="daily",
            confidence="maybe",
        )

    assert exc_info.value.fields == {
        "amount_cents": ["Must be greater than zero."],
        "frequency": ["Must be one of: one_time, weekly, biweekly, monthly."],
        "confidence": ["Must be one of: confirmed, unconfirmed."],
    }


def test_create_planned_expense_rejects_invalid_classification(db_session: Session) -> None:
    user = _create_user(db_session)

    with pytest.raises(FinancialInputValidationError) as exc_info:
        create_planned_expense_for_user(
            db_session,
            user_id=user.id,
            name="Rent",
            amount_cents=90000,
            next_date=date(2026, 9, 1),
            frequency="monthly",
            classification="required-ish",
        )

    assert exc_info.value.fields == {
        "classification": ["Must be one of: essential, discretionary."]
    }


def test_deactivate_income_source_returns_not_found_for_cross_user_access(
    db_session: Session,
) -> None:
    owner = _create_user(db_session, email_normalized="income-owner@example.com")
    other_user = _create_user(db_session, email_normalized="income-other@example.com")
    income = create_income_source_for_user(
        db_session,
        user_id=owner.id,
        name="Campus job",
        amount_cents=45000,
        next_date=date(2026, 8, 7),
        frequency="weekly",
        confidence="confirmed",
    )

    with pytest.raises(FinancialInputNotFoundError):
        deactivate_income_source_for_user(
            db_session,
            user_id=other_user.id,
            income_source_id=income.id,
        )


def test_deactivate_planned_expense_returns_not_found_for_cross_user_access(
    db_session: Session,
) -> None:
    owner = _create_user(db_session, email_normalized="expense-owner@example.com")
    other_user = _create_user(db_session, email_normalized="expense-other@example.com")
    expense = create_planned_expense_for_user(
        db_session,
        user_id=owner.id,
        name="Rent",
        amount_cents=90000,
        next_date=date(2026, 9, 1),
        frequency="monthly",
        classification="essential",
    )

    with pytest.raises(FinancialInputNotFoundError):
        deactivate_planned_expense_for_user(
            db_session,
            user_id=other_user.id,
            planned_expense_id=expense.id,
        )


def _create_user(
    db_session: Session,
    *,
    email_normalized: str = "nati@example.com",
) -> User:
    return create_user(
        db_session,
        email_normalized=email_normalized,
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
