"""Boundary between persisted financial inputs and pace-engine inputs."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from sqlalchemy.orm import Session

from app.models import FinancialProfile, Goal, IncomeSource, PlannedExpense
from app.pace_engine.types import (
    FORMULA_VERSION,
    ExpenseClassification,
    IncomeConfidence,
    IncomeSourceInput,
    PaceInput,
    PlannedExpenseInput,
    RecurrenceFrequency,
)
from app.repositories.financial_inputs import (
    get_financial_profile,
    list_active_income_sources,
    list_active_planned_expenses,
)
from app.repositories.goals import get_active_goal


class RecalculationStatus(StrEnum):
    READY = "ready"
    MISSING_INPUTS = "missing_inputs"


class MissingInput(StrEnum):
    ACTIVE_GOAL = "active_goal"
    FINANCIAL_PROFILE = "financial_profile"
    RESERVE_BUFFER_CONFIRMATION = "reserve_buffer_confirmation"


@dataclass(frozen=True, slots=True)
class RecalculationReadiness:
    status: RecalculationStatus
    missing_inputs: tuple[MissingInput, ...]
    pace_input: PaceInput | None
    goal: Goal | None = None
    financial_profile: FinancialProfile | None = None
    income_sources: tuple[IncomeSource, ...] = ()
    planned_expenses: tuple[PlannedExpense, ...] = ()


def prepare_pace_input_for_user(
    db_session: Session,
    *,
    user_id: str,
    user_time_zone: str,
    calculated_at: datetime,
) -> RecalculationReadiness:
    goal = get_active_goal(db_session, user_id=user_id)
    profile = get_financial_profile(db_session, user_id=user_id)

    missing_inputs: list[MissingInput] = []
    if goal is None:
        missing_inputs.append(MissingInput.ACTIVE_GOAL)
    if profile is None:
        missing_inputs.append(MissingInput.FINANCIAL_PROFILE)
    elif not profile.reserve_buffer_confirmed:
        missing_inputs.append(MissingInput.RESERVE_BUFFER_CONFIRMATION)

    if missing_inputs or goal is None or profile is None:
        return RecalculationReadiness(
            status=RecalculationStatus.MISSING_INPUTS,
            missing_inputs=tuple(missing_inputs),
            pace_input=None,
        )

    source_records = tuple(list_active_income_sources(db_session, user_id=user_id))
    expense_records = tuple(list_active_planned_expenses(db_session, user_id=user_id))

    income_sources = tuple(
        IncomeSourceInput(
            name=income_source.name,
            amount_cents=income_source.amount_cents,
            next_date=income_source.next_date,
            frequency=RecurrenceFrequency(income_source.frequency),
            confidence=IncomeConfidence(income_source.confidence),
            active=income_source.active,
        )
        for income_source in source_records
    )
    planned_expenses = tuple(
        PlannedExpenseInput(
            name=planned_expense.name,
            amount_cents=planned_expense.amount_cents,
            next_date=planned_expense.next_date,
            frequency=RecurrenceFrequency(planned_expense.frequency),
            classification=ExpenseClassification(planned_expense.classification),
            active=planned_expense.active,
        )
        for planned_expense in expense_records
    )

    return RecalculationReadiness(
        status=RecalculationStatus.READY,
        missing_inputs=(),
        pace_input=PaceInput(
            formula_version=FORMULA_VERSION,
            calculated_at=calculated_at,
            user_time_zone=user_time_zone,
            target_cents=goal.target_cents,
            initial_saved_cents=goal.initial_saved_cents,
            current_saved_cents=goal.current_saved_cents,
            start_date=goal.start_date,
            target_date=goal.target_date,
            starting_cash_cents=profile.starting_cash_cents,
            balance_as_of_date=profile.balance_as_of_date,
            reserve_buffer_cents=profile.reserve_buffer_cents,
            income_sources=income_sources,
            planned_expenses=planned_expenses,
        ),
        goal=goal,
        financial_profile=profile,
        income_sources=source_records,
        planned_expenses=expense_records,
    )
