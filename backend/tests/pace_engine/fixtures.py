from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

from app.pace_engine.types import (
    FORMULA_VERSION,
    IncomeConfidence,
    IncomeSourceInput,
    PaceInput,
    PaceResult,
    PaceStatus,
    PlannedExpenseInput,
    RecurrenceFrequency,
)


@dataclass(frozen=True, slots=True)
class GoldenScenario:
    name: str
    input_data: PaceInput
    expected_result: PaceResult


CALCULATED_AT = datetime(2026, 8, 1, 16, 0, tzinfo=UTC)
TIME_ZONE = "America/Los_Angeles"


def _input(
    *,
    target_cents: int = 100_000,
    initial_saved_cents: int = 0,
    current_saved_cents: int = 0,
    start_date: date = date(2026, 8, 1),
    target_date: date = date(2026, 9, 26),
    starting_cash_cents: int = 0,
    reserve_buffer_cents: int = 0,
    income_sources: tuple[IncomeSourceInput, ...] = (),
    planned_expenses: tuple[PlannedExpenseInput, ...] = (),
) -> PaceInput:
    return PaceInput(
        formula_version=FORMULA_VERSION,
        calculated_at=CALCULATED_AT,
        user_time_zone=TIME_ZONE,
        target_cents=target_cents,
        initial_saved_cents=initial_saved_cents,
        current_saved_cents=current_saved_cents,
        start_date=start_date,
        target_date=target_date,
        starting_cash_cents=starting_cash_cents,
        balance_as_of_date=date(2026, 8, 1),
        reserve_buffer_cents=reserve_buffer_cents,
        income_sources=income_sources,
        planned_expenses=planned_expenses,
    )


def _result(
    *,
    current_cash_cents: int,
    confirmed_future_income_cents: int,
    planned_future_expenses_cents: int,
    reserve_buffer_cents: int,
    forecast_resources_cents: int,
    goal_gap_cents: int,
    discretionary_capacity_cents: int,
    remaining_weeks: int,
    weekly_safe_to_spend_cents: int,
    projected_shortfall_cents: int,
    expected_savings_to_date_cents: int,
    pace_status: PaceStatus,
) -> PaceResult:
    return PaceResult(
        formula_version=FORMULA_VERSION,
        current_cash_cents=current_cash_cents,
        confirmed_future_income_cents=confirmed_future_income_cents,
        planned_future_expenses_cents=planned_future_expenses_cents,
        reserve_buffer_cents=reserve_buffer_cents,
        forecast_resources_cents=forecast_resources_cents,
        goal_gap_cents=goal_gap_cents,
        discretionary_capacity_cents=discretionary_capacity_cents,
        remaining_weeks=remaining_weeks,
        weekly_safe_to_spend_cents=weekly_safe_to_spend_cents,
        projected_shortfall_cents=projected_shortfall_cents,
        expected_savings_to_date_cents=expected_savings_to_date_cents,
        pace_status=pace_status,
    )


GOLDEN_SCENARIOS = (
    GoldenScenario(
        name="completed",
        input_data=_input(current_saved_cents=100_000),
        expected_result=_result(
            current_cash_cents=0,
            confirmed_future_income_cents=0,
            planned_future_expenses_cents=0,
            reserve_buffer_cents=0,
            forecast_resources_cents=0,
            goal_gap_cents=0,
            discretionary_capacity_cents=0,
            remaining_weeks=8,
            weekly_safe_to_spend_cents=0,
            projected_shortfall_cents=0,
            expected_savings_to_date_cents=0,
            pace_status=PaceStatus.COMPLETED,
        ),
    ),
    GoldenScenario(
        name="off_pace",
        input_data=_input(current_saved_cents=10_000, starting_cash_cents=20_000),
        expected_result=_result(
            current_cash_cents=20_000,
            confirmed_future_income_cents=0,
            planned_future_expenses_cents=0,
            reserve_buffer_cents=0,
            forecast_resources_cents=20_000,
            goal_gap_cents=90_000,
            discretionary_capacity_cents=-70_000,
            remaining_weeks=8,
            weekly_safe_to_spend_cents=0,
            projected_shortfall_cents=70_000,
            expected_savings_to_date_cents=0,
            pace_status=PaceStatus.OFF_PACE,
        ),
    ),
    GoldenScenario(
        name="ahead",
        input_data=_input(current_saved_cents=40_000, starting_cash_cents=100_000),
        expected_result=_result(
            current_cash_cents=100_000,
            confirmed_future_income_cents=0,
            planned_future_expenses_cents=0,
            reserve_buffer_cents=0,
            forecast_resources_cents=100_000,
            goal_gap_cents=60_000,
            discretionary_capacity_cents=40_000,
            remaining_weeks=8,
            weekly_safe_to_spend_cents=5_000,
            projected_shortfall_cents=0,
            expected_savings_to_date_cents=0,
            pace_status=PaceStatus.AHEAD,
        ),
    ),
    GoldenScenario(
        name="at_risk",
        input_data=_input(
            initial_saved_cents=0,
            current_saved_cents=25_000,
            start_date=date(2026, 7, 12),
            target_date=date(2026, 8, 21),
            starting_cash_cents=100_000,
        ),
        expected_result=_result(
            current_cash_cents=100_000,
            confirmed_future_income_cents=0,
            planned_future_expenses_cents=0,
            reserve_buffer_cents=0,
            forecast_resources_cents=100_000,
            goal_gap_cents=75_000,
            discretionary_capacity_cents=25_000,
            remaining_weeks=3,
            weekly_safe_to_spend_cents=8_300,
            projected_shortfall_cents=0,
            expected_savings_to_date_cents=50_000,
            pace_status=PaceStatus.AT_RISK,
        ),
    ),
    GoldenScenario(
        name="on_track",
        input_data=_input(
            initial_saved_cents=0,
            current_saved_cents=50_000,
            start_date=date(2026, 7, 12),
            target_date=date(2026, 8, 21),
            starting_cash_cents=100_000,
        ),
        expected_result=_result(
            current_cash_cents=100_000,
            confirmed_future_income_cents=0,
            planned_future_expenses_cents=0,
            reserve_buffer_cents=0,
            forecast_resources_cents=100_000,
            goal_gap_cents=50_000,
            discretionary_capacity_cents=50_000,
            remaining_weeks=3,
            weekly_safe_to_spend_cents=16_600,
            projected_shortfall_cents=0,
            expected_savings_to_date_cents=50_000,
            pace_status=PaceStatus.ON_TRACK,
        ),
    ),
    GoldenScenario(
        name="zero_confirmed_future_income",
        input_data=_input(current_saved_cents=20_000, starting_cash_cents=90_000),
        expected_result=_result(
            current_cash_cents=90_000,
            confirmed_future_income_cents=0,
            planned_future_expenses_cents=0,
            reserve_buffer_cents=0,
            forecast_resources_cents=90_000,
            goal_gap_cents=80_000,
            discretionary_capacity_cents=10_000,
            remaining_weeks=8,
            weekly_safe_to_spend_cents=1_200,
            projected_shortfall_cents=0,
            expected_savings_to_date_cents=0,
            pace_status=PaceStatus.AHEAD,
        ),
    ),
    GoldenScenario(
        name="fewer_than_seven_days_remaining",
        input_data=_input(
            current_saved_cents=20_000,
            target_date=date(2026, 8, 5),
            starting_cash_cents=90_000,
        ),
        expected_result=_result(
            current_cash_cents=90_000,
            confirmed_future_income_cents=0,
            planned_future_expenses_cents=0,
            reserve_buffer_cents=0,
            forecast_resources_cents=90_000,
            goal_gap_cents=80_000,
            discretionary_capacity_cents=10_000,
            remaining_weeks=1,
            weekly_safe_to_spend_cents=10_000,
            projected_shortfall_cents=0,
            expected_savings_to_date_cents=0,
            pace_status=PaceStatus.AHEAD,
        ),
    ),
    GoldenScenario(
        name="unconfirmed_income_excluded",
        input_data=_input(
            current_saved_cents=10_000,
            starting_cash_cents=20_000,
            income_sources=(
                IncomeSourceInput(
                    name="Possible bonus",
                    amount_cents=1_000_000,
                    next_date=date(2026, 8, 8),
                    frequency=RecurrenceFrequency.ONE_TIME,
                    confidence=IncomeConfidence.UNCONFIRMED,
                ),
            ),
        ),
        expected_result=_result(
            current_cash_cents=20_000,
            confirmed_future_income_cents=0,
            planned_future_expenses_cents=0,
            reserve_buffer_cents=0,
            forecast_resources_cents=20_000,
            goal_gap_cents=90_000,
            discretionary_capacity_cents=-70_000,
            remaining_weeks=8,
            weekly_safe_to_spend_cents=0,
            projected_shortfall_cents=70_000,
            expected_savings_to_date_cents=0,
            pace_status=PaceStatus.OFF_PACE,
        ),
    ),
    GoldenScenario(
        name="rounding_down_to_whole_dollars",
        input_data=_input(
            target_cents=1,
            current_saved_cents=0,
            starting_cash_cents=100_999,
            target_date=date(2026, 8, 15),
        ),
        expected_result=_result(
            current_cash_cents=100_999,
            confirmed_future_income_cents=0,
            planned_future_expenses_cents=0,
            reserve_buffer_cents=0,
            forecast_resources_cents=100_999,
            goal_gap_cents=1,
            discretionary_capacity_cents=100_998,
            remaining_weeks=2,
            weekly_safe_to_spend_cents=50_400,
            projected_shortfall_cents=0,
            expected_savings_to_date_cents=0,
            pace_status=PaceStatus.ON_TRACK,
        ),
    ),
)


RESERVE_BUFFER_SUGGESTION_EXAMPLES = (
    (0, 0),
    (100_000, 5_000),
    (100_001, 5_100),
    (1, 100),
)
