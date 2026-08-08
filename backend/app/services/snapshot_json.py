"""Build immutable calculation snapshot JSON payloads."""

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any

from app.models import (
    CalculationSnapshot,
    FinancialProfile,
    Goal,
    IncomeSource,
    PlannedExpense,
)
from app.pace_engine.types import PaceResult

SNAPSHOT_INPUT_SCHEMA_VERSION = "snapshot-input-v1"
SNAPSHOT_RESULT_SCHEMA_VERSION = "snapshot-result-v1"


@dataclass(frozen=True, slots=True)
class SnapshotJsonPayload:
    normalized_input_json: dict[str, Any]
    result_json: dict[str, Any]


def build_snapshot_json(
    *,
    trigger: str,
    calculated_at: datetime,
    user_time_zone: str,
    goal: Goal,
    financial_profile: FinancialProfile,
    income_sources: tuple[IncomeSource, ...],
    planned_expenses: tuple[PlannedExpense, ...],
    pace_result: PaceResult,
    previous_snapshot: CalculationSnapshot | None,
) -> SnapshotJsonPayload:
    normalized_input_json = _normalized_input_json(
        trigger=trigger,
        calculated_at=calculated_at,
        user_time_zone=user_time_zone,
        goal=goal,
        financial_profile=financial_profile,
        income_sources=income_sources,
        planned_expenses=planned_expenses,
        formula_version=pace_result.formula_version,
    )
    return SnapshotJsonPayload(
        normalized_input_json=normalized_input_json,
        result_json=_result_json(
            goal=goal,
            income_sources=income_sources,
            planned_expenses=planned_expenses,
            pace_result=pace_result,
            previous_snapshot=previous_snapshot,
            normalized_input_json=normalized_input_json,
        ),
    )


def _normalized_input_json(
    *,
    trigger: str,
    calculated_at: datetime,
    user_time_zone: str,
    goal: Goal,
    financial_profile: FinancialProfile,
    income_sources: tuple[IncomeSource, ...],
    planned_expenses: tuple[PlannedExpense, ...],
    formula_version: str,
) -> dict[str, Any]:
    return {
        "schema_version": SNAPSHOT_INPUT_SCHEMA_VERSION,
        "formula_version": formula_version,
        "calculation": {
            "timestamp_utc": _utc_timestamp(calculated_at),
            "user_time_zone": user_time_zone,
            "trigger": trigger,
        },
        "goal": {
            "id": goal.id,
            "name": goal.name,
            "target_cents": goal.target_cents,
            "initial_saved_cents": goal.initial_saved_cents,
            "current_saved_cents": goal.current_saved_cents,
            "start_date": _date_string(goal.start_date),
            "target_date": _date_string(goal.target_date),
            "status": goal.status,
        },
        "financial_profile": {
            "starting_cash_cents": financial_profile.starting_cash_cents,
            "balance_as_of_date": _date_string(financial_profile.balance_as_of_date),
            "reserve_buffer_cents": financial_profile.reserve_buffer_cents,
            "reserve_buffer_confirmed": financial_profile.reserve_buffer_confirmed,
        },
        "income_sources": [
            _income_source_json(income_source) for income_source in income_sources
        ],
        "planned_expenses": [
            _planned_expense_json(planned_expense)
            for planned_expense in planned_expenses
        ],
        "transactions": [],
    }


def _result_json(
    *,
    goal: Goal,
    income_sources: tuple[IncomeSource, ...],
    planned_expenses: tuple[PlannedExpense, ...],
    pace_result: PaceResult,
    previous_snapshot: CalculationSnapshot | None,
    normalized_input_json: dict[str, Any],
) -> dict[str, Any]:
    weekly_safe_to_spend_cents = pace_result.weekly_safe_to_spend_cents
    return {
        "schema_version": SNAPSHOT_RESULT_SCHEMA_VERSION,
        "formula_version": pace_result.formula_version,
        "outputs": {
            "current_cash_cents": pace_result.current_cash_cents,
            "confirmed_future_income_cents": pace_result.confirmed_future_income_cents,
            "planned_future_expenses_cents": pace_result.planned_future_expenses_cents,
            "reserve_buffer_cents": pace_result.reserve_buffer_cents,
            "forecast_resources_cents": pace_result.forecast_resources_cents,
            "goal_gap_cents": pace_result.goal_gap_cents,
            "discretionary_capacity_cents": pace_result.discretionary_capacity_cents,
            "remaining_weeks": pace_result.remaining_weeks,
            "weekly_safe_to_spend_cents": weekly_safe_to_spend_cents,
            "projected_shortfall_cents": pace_result.projected_shortfall_cents,
            "expected_savings_to_date_cents": pace_result.expected_savings_to_date_cents,
            "pace_status": pace_result.pace_status.value,
            "progress_percentage": _progress_percentage(goal),
            "current_week_opening_allowance_cents": weekly_safe_to_spend_cents,
            "current_week_remainder_cents": weekly_safe_to_spend_cents,
        },
        "explanation": _explanation_json(
            income_sources=income_sources,
            planned_expenses=planned_expenses,
        ),
        "changed_from_previous": _changed_from_previous_json(
            previous_snapshot=previous_snapshot,
            normalized_input_json=normalized_input_json,
            weekly_safe_to_spend_cents=weekly_safe_to_spend_cents,
        ),
    }


def _income_source_json(income_source: IncomeSource) -> dict[str, Any]:
    return {
        "id": income_source.id,
        "name": income_source.name,
        "amount_cents": income_source.amount_cents,
        "next_date": _date_string(income_source.next_date),
        "frequency": income_source.frequency,
        "confidence": income_source.confidence,
        "active": income_source.active,
    }


def _planned_expense_json(planned_expense: PlannedExpense) -> dict[str, Any]:
    return {
        "id": planned_expense.id,
        "name": planned_expense.name,
        "amount_cents": planned_expense.amount_cents,
        "next_date": _date_string(planned_expense.next_date),
        "frequency": planned_expense.frequency,
        "classification": planned_expense.classification,
        "active": planned_expense.active,
    }


def _explanation_json(
    *,
    income_sources: tuple[IncomeSource, ...],
    planned_expenses: tuple[PlannedExpense, ...],
) -> dict[str, Any]:
    included_income_ids = [
        income_source.id
        for income_source in income_sources
        if income_source.active and income_source.confidence == "confirmed"
    ]
    excluded_income_ids = [
        income_source.id
        for income_source in income_sources
        if not income_source.active or income_source.confidence != "confirmed"
    ]
    included_expense_ids = [
        planned_expense.id for planned_expense in planned_expenses if planned_expense.active
    ]
    excluded_expense_ids = [
        planned_expense.id
        for planned_expense in planned_expenses
        if not planned_expense.active
    ]
    return {
        "included_income_source_ids": included_income_ids,
        "excluded_income_source_ids": excluded_income_ids,
        "included_planned_expense_ids": included_expense_ids,
        "excluded_planned_expense_ids": excluded_expense_ids,
        "summary": {
            "confirmed_income_count": len(included_income_ids),
            "planned_expense_count": len(included_expense_ids),
            "unconfirmed_income_count": sum(
                1
                for income_source in income_sources
                if income_source.active and income_source.confidence == "unconfirmed"
            ),
        },
    }


def _changed_from_previous_json(
    *,
    previous_snapshot: CalculationSnapshot | None,
    normalized_input_json: dict[str, Any],
    weekly_safe_to_spend_cents: int,
) -> dict[str, Any]:
    if previous_snapshot is None:
        return {
            "previous_snapshot_id": None,
            "changed_input_categories": [],
            "weekly_safe_to_spend_delta_cents": None,
        }

    return {
        "previous_snapshot_id": previous_snapshot.id,
        "changed_input_categories": _changed_input_categories(
            previous_snapshot.normalized_input_json,
            normalized_input_json,
        ),
        "weekly_safe_to_spend_delta_cents": weekly_safe_to_spend_cents
        - _previous_weekly_safe_to_spend_cents(previous_snapshot),
    }


def _changed_input_categories(
    previous_input_json: dict[str, Any],
    current_input_json: dict[str, Any],
) -> list[str]:
    categories = [
        "goal",
        "financial_profile",
        "income_sources",
        "planned_expenses",
        "transactions",
    ]
    return [
        category
        for category in categories
        if previous_input_json.get(category) != current_input_json.get(category)
    ]


def _previous_weekly_safe_to_spend_cents(snapshot: CalculationSnapshot) -> int:
    outputs = snapshot.result_json.get("outputs", {})
    value = outputs.get("weekly_safe_to_spend_cents", 0)
    if not isinstance(value, int):
        return 0
    return value


def _progress_percentage(goal: Goal) -> float:
    if goal.target_cents <= 0:
        return 0.0
    return round((goal.current_saved_cents / goal.target_cents) * 100, 2)


def _utc_timestamp(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _date_string(value: date) -> str:
    return value.isoformat()
