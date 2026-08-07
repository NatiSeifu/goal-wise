from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from app.pace_engine.calculator import (
    calculation_local_date,
    confirmed_future_income_cents,
    current_cash_cents,
    discretionary_capacity_cents,
    forecast_resources_cents,
    future_occurrence_dates,
    goal_gap_cents,
    planned_future_expenses_cents,
    projected_shortfall_cents,
    remaining_weeks,
    suggest_reserve_buffer_cents,
    weekly_safe_to_spend_cents,
)
from app.pace_engine.types import (
    FORMULA_VERSION,
    ExpenseClassification,
    IncomeConfidence,
    IncomeSourceInput,
    PaceInput,
    PlannedExpenseInput,
    RecurrenceFrequency,
)


def _base_input(
    *,
    calculated_at: datetime = datetime(2026, 8, 7, 16, 0, tzinfo=UTC),
    income_sources: tuple[IncomeSourceInput, ...] = (),
    planned_expenses: tuple[PlannedExpenseInput, ...] = (),
    target_date: date = date(2026, 8, 31),
) -> PaceInput:
    return PaceInput(
        formula_version=FORMULA_VERSION,
        calculated_at=calculated_at,
        user_time_zone="America/Los_Angeles",
        target_cents=100_000,
        initial_saved_cents=10_000,
        current_saved_cents=25_000,
        start_date=date(2026, 8, 1),
        target_date=target_date,
        starting_cash_cents=50_000,
        balance_as_of_date=date(2026, 8, 6),
        reserve_buffer_cents=5_000,
        income_sources=income_sources,
        planned_expenses=planned_expenses,
    )


def test_calculation_local_date_uses_user_time_zone() -> None:
    calculated_at = datetime(2026, 8, 8, 6, 30, tzinfo=UTC)

    assert calculation_local_date(calculated_at, "America/Los_Angeles") == date(2026, 8, 7)


def test_future_occurrences_exclude_same_day_and_after_target() -> None:
    calculated_at = datetime(2026, 8, 7, 16, 0, tzinfo=UTC)

    assert (
        future_occurrence_dates(
            next_date=date(2026, 8, 7),
            frequency=RecurrenceFrequency.ONE_TIME,
            calculated_at=calculated_at,
            user_time_zone="America/Los_Angeles",
            target_date=date(2026, 8, 31),
        )
        == ()
    )
    assert (
        future_occurrence_dates(
            next_date=date(2026, 9, 1),
            frequency=RecurrenceFrequency.ONE_TIME,
            calculated_at=calculated_at,
            user_time_zone="America/Los_Angeles",
            target_date=date(2026, 8, 31),
        )
        == ()
    )


@pytest.mark.parametrize(
    ("frequency", "expected"),
    [
        (RecurrenceFrequency.ONE_TIME, (date(2026, 8, 8),)),
        (
            RecurrenceFrequency.WEEKLY,
            (date(2026, 8, 8), date(2026, 8, 15), date(2026, 8, 22), date(2026, 8, 29)),
        ),
        (RecurrenceFrequency.BIWEEKLY, (date(2026, 8, 8), date(2026, 8, 22))),
    ],
)
def test_future_occurrences_include_supported_frequencies(
    frequency: RecurrenceFrequency, expected: tuple[date, ...]
) -> None:
    assert (
        future_occurrence_dates(
            next_date=date(2026, 8, 8),
            frequency=frequency,
            calculated_at=datetime(2026, 8, 7, 16, 0, tzinfo=UTC),
            user_time_zone="America/Los_Angeles",
            target_date=date(2026, 8, 31),
        )
        == expected
    )


def test_monthly_recurrence_uses_last_day_when_month_is_shorter() -> None:
    assert future_occurrence_dates(
        next_date=date(2026, 1, 31),
        frequency=RecurrenceFrequency.MONTHLY,
        calculated_at=datetime(2026, 1, 1, 16, 0, tzinfo=UTC),
        user_time_zone="America/Los_Angeles",
        target_date=date(2026, 3, 31),
    ) == (date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31))


def test_monthly_recurrence_handles_leap_year_february() -> None:
    assert future_occurrence_dates(
        next_date=date(2028, 1, 31),
        frequency=RecurrenceFrequency.MONTHLY,
        calculated_at=datetime(2028, 1, 1, 16, 0, tzinfo=UTC),
        user_time_zone="America/Los_Angeles",
        target_date=date(2028, 3, 31),
    ) == (date(2028, 1, 31), date(2028, 2, 29), date(2028, 3, 31))


def test_confirmed_future_income_excludes_unconfirmed_and_inactive_sources() -> None:
    input_data = _base_input(
        income_sources=(
            IncomeSourceInput(
                name="Confirmed",
                amount_cents=100_000,
                next_date=date(2026, 8, 14),
                frequency=RecurrenceFrequency.WEEKLY,
                confidence=IncomeConfidence.CONFIRMED,
            ),
            IncomeSourceInput(
                name="Unconfirmed",
                amount_cents=500_000,
                next_date=date(2026, 8, 14),
                frequency=RecurrenceFrequency.WEEKLY,
                confidence=IncomeConfidence.UNCONFIRMED,
            ),
            IncomeSourceInput(
                name="Inactive",
                amount_cents=250_000,
                next_date=date(2026, 8, 14),
                frequency=RecurrenceFrequency.WEEKLY,
                confidence=IncomeConfidence.CONFIRMED,
                active=False,
            ),
        )
    )

    assert confirmed_future_income_cents(input_data) == 300_000


def test_planned_future_expenses_excludes_inactive_expenses() -> None:
    input_data = _base_input(
        planned_expenses=(
            PlannedExpenseInput(
                name="Rent",
                amount_cents=150_000,
                next_date=date(2026, 8, 14),
                frequency=RecurrenceFrequency.ONE_TIME,
                classification=ExpenseClassification.ESSENTIAL,
            ),
            PlannedExpenseInput(
                name="Inactive",
                amount_cents=999_999,
                next_date=date(2026, 8, 14),
                frequency=RecurrenceFrequency.ONE_TIME,
                classification=ExpenseClassification.DISCRETIONARY,
                active=False,
            ),
        )
    )

    assert planned_future_expenses_cents(input_data) == 150_000


def test_core_money_formulas() -> None:
    assert current_cash_cents(_base_input()) == 50_000
    assert (
        forecast_resources_cents(
            current_cash_cents=50_000,
            confirmed_future_income_cents=300_000,
            planned_future_expenses_cents=150_000,
            reserve_buffer_cents=5_000,
        )
        == 195_000
    )
    assert goal_gap_cents(target_cents=100_000, current_saved_cents=25_000) == 75_000
    assert goal_gap_cents(target_cents=100_000, current_saved_cents=100_001) == 0
    assert (
        discretionary_capacity_cents(forecast_resources_cents=195_000, goal_gap_cents=75_000)
        == 120_000
    )
    assert (
        projected_shortfall_cents(goal_gap_cents=75_000, forecast_resources_cents=70_000) == 5_000
    )
    assert projected_shortfall_cents(goal_gap_cents=75_000, forecast_resources_cents=75_000) == 0


@pytest.mark.parametrize(
    ("calculated_at", "target_date", "expected"),
    [
        (datetime(2026, 8, 7, 16, 0, tzinfo=UTC), date(2026, 8, 8), 1),
        (datetime(2026, 8, 7, 16, 0, tzinfo=UTC), date(2026, 8, 14), 1),
        (datetime(2026, 8, 7, 16, 0, tzinfo=UTC), date(2026, 8, 15), 2),
        (datetime(2026, 8, 7, 16, 0, tzinfo=UTC), date(2026, 8, 7), 1),
    ],
)
def test_remaining_weeks_never_below_one(
    calculated_at: datetime, target_date: date, expected: int
) -> None:
    assert remaining_weeks(calculated_at, "America/Los_Angeles", target_date) == expected


@pytest.mark.parametrize(
    ("capacity", "weeks", "expected"),
    [
        (100_999, 10, 10_000),
        (10_750, 2, 5_300),
        (-10_000, 4, 0),
    ],
)
def test_weekly_safe_to_spend_rounds_down_to_whole_dollars(
    capacity: int, weeks: int, expected: int
) -> None:
    assert weekly_safe_to_spend_cents(capacity, weeks) == expected


@pytest.mark.parametrize(
    ("confirmed_income", "expected"),
    [
        (0, 0),
        (100_000, 5_000),
        (100_001, 5_100),
        (1, 100),
    ],
)
def test_reserve_buffer_suggestion_uses_confirmed_income_and_rounds_up(
    confirmed_income: int, expected: int
) -> None:
    assert suggest_reserve_buffer_cents(confirmed_income) == expected
