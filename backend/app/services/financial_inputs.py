"""Financial input service behavior."""

from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models import FinancialProfile, IncomeSource, PlannedExpense
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
from app.services.local_dates import user_local_date

ALLOWED_FREQUENCIES = ("one_time", "weekly", "biweekly", "monthly")
ALLOWED_INCOME_CONFIDENCE = ("confirmed", "unconfirmed")
ALLOWED_EXPENSE_CLASSIFICATIONS = ("essential", "discretionary")


class FinancialInputError(Exception):
    """Base class for expected financial input service failures."""


class FinancialInputValidationError(FinancialInputError):
    def __init__(self, fields: dict[str, list[str]]) -> None:
        self.fields = fields
        super().__init__("Financial input validation failed.")


class FinancialInputNotFoundError(FinancialInputError):
    """Raised when a financial input record does not exist for the user."""


def get_financial_profile_for_user(
    db_session: Session,
    *,
    user_id: str,
) -> FinancialProfile | None:
    return get_financial_profile(db_session, user_id=user_id)


def upsert_financial_profile_for_user(
    db_session: Session,
    *,
    user_id: str,
    starting_cash_cents: int,
    balance_as_of_date: date,
    reserve_buffer_cents: int,
    reserve_buffer_confirmed: bool,
    user_time_zone: str,
    now: datetime,
) -> FinancialProfile:
    fields: dict[str, list[str]] = {}
    if starting_cash_cents < 0:
        fields.setdefault("starting_cash_cents", []).append(
            "Must be greater than or equal to zero.",
        )
    if reserve_buffer_cents < 0:
        fields.setdefault("reserve_buffer_cents", []).append(
            "Must be greater than or equal to zero.",
        )
    if balance_as_of_date > user_local_date(now=now, user_time_zone=user_time_zone):
        fields.setdefault("balance_as_of_date", []).append(
            "Cannot be after the user's current local date.",
        )
    if fields:
        raise FinancialInputValidationError(fields)

    return upsert_financial_profile(
        db_session,
        user_id=user_id,
        starting_cash_cents=starting_cash_cents,
        balance_as_of_date=balance_as_of_date,
        reserve_buffer_cents=reserve_buffer_cents,
        reserve_buffer_confirmed=reserve_buffer_confirmed,
    )


def list_income_sources_for_user(db_session: Session, *, user_id: str) -> list[IncomeSource]:
    return list_active_income_sources(db_session, user_id=user_id)


def create_income_source_for_user(
    db_session: Session,
    *,
    user_id: str,
    name: str,
    amount_cents: int,
    next_date: date,
    frequency: str,
    confidence: str,
) -> IncomeSource:
    fields = _validate_shared_source_fields(
        name=name,
        amount_cents=amount_cents,
        frequency=frequency,
    )
    if confidence not in ALLOWED_INCOME_CONFIDENCE:
        fields.setdefault("confidence", []).append(_one_of_message(ALLOWED_INCOME_CONFIDENCE))
    if fields:
        raise FinancialInputValidationError(fields)

    return create_income_source(
        db_session,
        user_id=user_id,
        name=name.strip(),
        amount_cents=amount_cents,
        next_date=next_date,
        frequency=frequency,
        confidence=confidence,
    )


def update_income_source_for_user(
    db_session: Session,
    *,
    user_id: str,
    income_source_id: str,
    name: str,
    amount_cents: int,
    next_date: date,
    frequency: str,
    confidence: str,
) -> IncomeSource:
    income_source = get_income_source_for_user(
        db_session,
        user_id=user_id,
        income_source_id=income_source_id,
    )
    if income_source is None:
        raise FinancialInputNotFoundError

    fields = _validate_shared_source_fields(
        name=name,
        amount_cents=amount_cents,
        frequency=frequency,
    )
    if confidence not in ALLOWED_INCOME_CONFIDENCE:
        fields.setdefault("confidence", []).append(_one_of_message(ALLOWED_INCOME_CONFIDENCE))
    if fields:
        raise FinancialInputValidationError(fields)

    return update_income_source(
        db_session,
        income_source=income_source,
        name=name.strip(),
        amount_cents=amount_cents,
        next_date=next_date,
        frequency=frequency,
        confidence=confidence,
    )


def deactivate_income_source_for_user(
    db_session: Session,
    *,
    user_id: str,
    income_source_id: str,
) -> IncomeSource:
    income_source = get_income_source_for_user(
        db_session,
        user_id=user_id,
        income_source_id=income_source_id,
    )
    if income_source is None:
        raise FinancialInputNotFoundError

    return deactivate_income_source(db_session, income_source=income_source)


def list_planned_expenses_for_user(db_session: Session, *, user_id: str) -> list[PlannedExpense]:
    return list_active_planned_expenses(db_session, user_id=user_id)


def create_planned_expense_for_user(
    db_session: Session,
    *,
    user_id: str,
    name: str,
    amount_cents: int,
    next_date: date,
    frequency: str,
    classification: str,
) -> PlannedExpense:
    fields = _validate_shared_source_fields(
        name=name,
        amount_cents=amount_cents,
        frequency=frequency,
    )
    if classification not in ALLOWED_EXPENSE_CLASSIFICATIONS:
        fields.setdefault("classification", []).append(
            _one_of_message(ALLOWED_EXPENSE_CLASSIFICATIONS),
        )
    if fields:
        raise FinancialInputValidationError(fields)

    return create_planned_expense(
        db_session,
        user_id=user_id,
        name=name.strip(),
        amount_cents=amount_cents,
        next_date=next_date,
        frequency=frequency,
        classification=classification,
    )


def update_planned_expense_for_user(
    db_session: Session,
    *,
    user_id: str,
    planned_expense_id: str,
    name: str,
    amount_cents: int,
    next_date: date,
    frequency: str,
    classification: str,
) -> PlannedExpense:
    planned_expense = get_planned_expense_for_user(
        db_session,
        user_id=user_id,
        planned_expense_id=planned_expense_id,
    )
    if planned_expense is None:
        raise FinancialInputNotFoundError

    fields = _validate_shared_source_fields(
        name=name,
        amount_cents=amount_cents,
        frequency=frequency,
    )
    if classification not in ALLOWED_EXPENSE_CLASSIFICATIONS:
        fields.setdefault("classification", []).append(
            _one_of_message(ALLOWED_EXPENSE_CLASSIFICATIONS),
        )
    if fields:
        raise FinancialInputValidationError(fields)

    return update_planned_expense(
        db_session,
        planned_expense=planned_expense,
        name=name.strip(),
        amount_cents=amount_cents,
        next_date=next_date,
        frequency=frequency,
        classification=classification,
    )


def deactivate_planned_expense_for_user(
    db_session: Session,
    *,
    user_id: str,
    planned_expense_id: str,
) -> PlannedExpense:
    planned_expense = get_planned_expense_for_user(
        db_session,
        user_id=user_id,
        planned_expense_id=planned_expense_id,
    )
    if planned_expense is None:
        raise FinancialInputNotFoundError

    return deactivate_planned_expense(db_session, planned_expense=planned_expense)


def _validate_shared_source_fields(
    *,
    name: str,
    amount_cents: int,
    frequency: str,
) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    if not name.strip():
        fields.setdefault("name", []).append("Must not be blank.")
    if len(name.strip()) > 120:
        fields.setdefault("name", []).append("Must be 120 characters or fewer.")
    if amount_cents <= 0:
        fields.setdefault("amount_cents", []).append("Must be greater than zero.")
    if frequency not in ALLOWED_FREQUENCIES:
        fields.setdefault("frequency", []).append(_one_of_message(ALLOWED_FREQUENCIES))
    return fields


def _one_of_message(allowed_values: tuple[str, ...]) -> str:
    return f"Must be one of: {', '.join(allowed_values)}."
