"""Financial input persistence queries."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FinancialProfile, IncomeSource, PlannedExpense


def get_financial_profile(
    db_session: Session,
    *,
    user_id: str,
) -> FinancialProfile | None:
    return db_session.scalar(
        select(FinancialProfile).where(FinancialProfile.user_id == user_id),
    )


def upsert_financial_profile(
    db_session: Session,
    *,
    user_id: str,
    starting_cash_cents: int,
    balance_as_of_date: date,
    reserve_buffer_cents: int,
    reserve_buffer_confirmed: bool,
) -> FinancialProfile:
    profile = get_financial_profile(db_session, user_id=user_id)

    if profile is None:
        profile = FinancialProfile(
            user_id=user_id,
            starting_cash_cents=starting_cash_cents,
            balance_as_of_date=balance_as_of_date,
            reserve_buffer_cents=reserve_buffer_cents,
            reserve_buffer_confirmed=reserve_buffer_confirmed,
        )
        db_session.add(profile)
    else:
        profile.starting_cash_cents = starting_cash_cents
        profile.balance_as_of_date = balance_as_of_date
        profile.reserve_buffer_cents = reserve_buffer_cents
        profile.reserve_buffer_confirmed = reserve_buffer_confirmed

    db_session.flush()
    return profile


def create_income_source(
    db_session: Session,
    *,
    user_id: str,
    name: str,
    amount_cents: int,
    next_date: date,
    frequency: str,
    confidence: str,
) -> IncomeSource:
    income_source = IncomeSource(
        user_id=user_id,
        name=name,
        amount_cents=amount_cents,
        next_date=next_date,
        frequency=frequency,
        confidence=confidence,
        active=True,
    )
    db_session.add(income_source)
    db_session.flush()
    return income_source


def get_income_source_for_user(
    db_session: Session,
    *,
    user_id: str,
    income_source_id: str,
) -> IncomeSource | None:
    return db_session.scalar(
        select(IncomeSource).where(
            IncomeSource.id == income_source_id,
            IncomeSource.user_id == user_id,
        ),
    )


def list_active_income_sources(
    db_session: Session,
    *,
    user_id: str,
) -> list[IncomeSource]:
    return list(
        db_session.scalars(
            select(IncomeSource)
            .where(
                IncomeSource.user_id == user_id,
                IncomeSource.active.is_(True),
            )
            .order_by(IncomeSource.created_at, IncomeSource.id),
        ),
    )


def update_income_source(
    db_session: Session,
    *,
    income_source: IncomeSource,
    name: str,
    amount_cents: int,
    next_date: date,
    frequency: str,
    confidence: str,
) -> IncomeSource:
    income_source.name = name
    income_source.amount_cents = amount_cents
    income_source.next_date = next_date
    income_source.frequency = frequency
    income_source.confidence = confidence
    db_session.flush()
    return income_source


def deactivate_income_source(
    db_session: Session,
    *,
    income_source: IncomeSource,
) -> IncomeSource:
    income_source.active = False
    db_session.flush()
    return income_source


def create_planned_expense(
    db_session: Session,
    *,
    user_id: str,
    name: str,
    amount_cents: int,
    next_date: date,
    frequency: str,
    classification: str,
) -> PlannedExpense:
    planned_expense = PlannedExpense(
        user_id=user_id,
        name=name,
        amount_cents=amount_cents,
        next_date=next_date,
        frequency=frequency,
        classification=classification,
        active=True,
    )
    db_session.add(planned_expense)
    db_session.flush()
    return planned_expense


def get_planned_expense_for_user(
    db_session: Session,
    *,
    user_id: str,
    planned_expense_id: str,
) -> PlannedExpense | None:
    return db_session.scalar(
        select(PlannedExpense).where(
            PlannedExpense.id == planned_expense_id,
            PlannedExpense.user_id == user_id,
        ),
    )


def list_active_planned_expenses(
    db_session: Session,
    *,
    user_id: str,
) -> list[PlannedExpense]:
    return list(
        db_session.scalars(
            select(PlannedExpense)
            .where(
                PlannedExpense.user_id == user_id,
                PlannedExpense.active.is_(True),
            )
            .order_by(PlannedExpense.created_at, PlannedExpense.id),
        ),
    )


def update_planned_expense(
    db_session: Session,
    *,
    planned_expense: PlannedExpense,
    name: str,
    amount_cents: int,
    next_date: date,
    frequency: str,
    classification: str,
) -> PlannedExpense:
    planned_expense.name = name
    planned_expense.amount_cents = amount_cents
    planned_expense.next_date = next_date
    planned_expense.frequency = frequency
    planned_expense.classification = classification
    db_session.flush()
    return planned_expense


def deactivate_planned_expense(
    db_session: Session,
    *,
    planned_expense: PlannedExpense,
) -> PlannedExpense:
    planned_expense.active = False
    db_session.flush()
    return planned_expense
