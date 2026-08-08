from datetime import date

import pytest
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.repositories.auth import create_user
from app.repositories.financial_inputs import (
    create_income_source,
    create_planned_expense,
    deactivate_income_source,
    deactivate_planned_expense,
    get_financial_profile,
    get_income_source_for_user,
    get_planned_expense_for_user,
    list_active_income_sources,
    list_active_planned_expenses,
    update_income_source,
    update_planned_expense,
    upsert_financial_profile,
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


def test_upsert_financial_profile_creates_then_updates_one_record(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="profile@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )

    created_profile = upsert_financial_profile(
        db_session,
        user_id=user.id,
        starting_cash_cents=120000,
        balance_as_of_date=date(2026, 8, 1),
        reserve_buffer_cents=5000,
        reserve_buffer_confirmed=False,
    )
    updated_profile = upsert_financial_profile(
        db_session,
        user_id=user.id,
        starting_cash_cents=125000,
        balance_as_of_date=date(2026, 8, 2),
        reserve_buffer_cents=7500,
        reserve_buffer_confirmed=True,
    )
    db_session.commit()

    assert updated_profile.id == created_profile.id
    assert updated_profile.starting_cash_cents == 125000
    assert updated_profile.reserve_buffer_confirmed is True
    assert get_financial_profile(db_session, user_id=user.id) == updated_profile


def test_income_source_repository_filters_and_deactivates_by_user(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="income-owner@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    other_user = create_user(
        db_session,
        email_normalized="income-other@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    income = create_income_source(
        db_session,
        user_id=user.id,
        name="Campus job",
        amount_cents=45000,
        next_date=date(2026, 8, 7),
        frequency="weekly",
        confidence="confirmed",
    )
    create_income_source(
        db_session,
        user_id=other_user.id,
        name="Other job",
        amount_cents=50000,
        next_date=date(2026, 8, 8),
        frequency="weekly",
        confidence="confirmed",
    )
    db_session.commit()

    assert list_active_income_sources(db_session, user_id=user.id) == [income]
    assert (
        get_income_source_for_user(
            db_session,
            user_id=other_user.id,
            income_source_id=income.id,
        )
        is None
    )

    deactivate_income_source(db_session, income_source=income)
    db_session.commit()

    assert list_active_income_sources(db_session, user_id=user.id) == []


def test_update_income_source_changes_owned_record(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="income-update@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    income = create_income_source(
        db_session,
        user_id=user.id,
        name="Old income",
        amount_cents=45000,
        next_date=date(2026, 8, 7),
        frequency="weekly",
        confidence="unconfirmed",
    )

    updated_income = update_income_source(
        db_session,
        income_source=income,
        name="New income",
        amount_cents=60000,
        next_date=date(2026, 8, 14),
        frequency="biweekly",
        confidence="confirmed",
    )
    db_session.commit()

    assert updated_income.name == "New income"
    assert updated_income.amount_cents == 60000
    assert updated_income.confidence == "confirmed"


def test_planned_expense_repository_filters_and_deactivates_by_user(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="expense-owner@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    other_user = create_user(
        db_session,
        email_normalized="expense-other@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
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
    create_planned_expense(
        db_session,
        user_id=other_user.id,
        name="Other rent",
        amount_cents=80000,
        next_date=date(2026, 9, 1),
        frequency="monthly",
        classification="essential",
    )
    db_session.commit()

    assert list_active_planned_expenses(db_session, user_id=user.id) == [expense]
    assert (
        get_planned_expense_for_user(
            db_session,
            user_id=other_user.id,
            planned_expense_id=expense.id,
        )
        is None
    )

    deactivate_planned_expense(db_session, planned_expense=expense)
    db_session.commit()

    assert list_active_planned_expenses(db_session, user_id=user.id) == []


def test_update_planned_expense_changes_owned_record(db_session: Session) -> None:
    user = create_user(
        db_session,
        email_normalized="expense-update@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    expense = create_planned_expense(
        db_session,
        user_id=user.id,
        name="Old expense",
        amount_cents=90000,
        next_date=date(2026, 9, 1),
        frequency="monthly",
        classification="essential",
    )

    updated_expense = update_planned_expense(
        db_session,
        planned_expense=expense,
        name="New expense",
        amount_cents=3000,
        next_date=date(2026, 8, 10),
        frequency="weekly",
        classification="discretionary",
    )
    db_session.commit()

    assert updated_expense.name == "New expense"
    assert updated_expense.amount_cents == 3000
    assert updated_expense.classification == "discretionary"
