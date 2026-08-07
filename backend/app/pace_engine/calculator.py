from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.pace_engine.types import IncomeConfidence, PaceInput, PaceStatus, RecurrenceFrequency

# Date and recurrence helpers


def calculation_local_date(calculated_at: datetime, user_time_zone: str) -> date:
    return calculated_at.astimezone(ZoneInfo(user_time_zone)).date()


def future_occurrence_dates(
    *,
    next_date: date,
    frequency: RecurrenceFrequency,
    calculated_at: datetime,
    user_time_zone: str,
    target_date: date,
) -> tuple[date, ...]:
    local_date = calculation_local_date(calculated_at, user_time_zone)
    return tuple(
        occurrence_date
        for occurrence_date in _expand_occurrences(next_date, frequency, target_date)
        if local_date < occurrence_date <= target_date
    )


def current_cash_cents(input_data: PaceInput) -> int:
    return input_data.starting_cash_cents


# Aggregate and money helpers


def confirmed_future_income_cents(input_data: PaceInput) -> int:
    return sum(
        income.amount_cents
        * len(
            future_occurrence_dates(
                next_date=income.next_date,
                frequency=income.frequency,
                calculated_at=input_data.calculated_at,
                user_time_zone=input_data.user_time_zone,
                target_date=input_data.target_date,
            )
        )
        for income in input_data.income_sources
        if income.active and income.confidence is IncomeConfidence.CONFIRMED
    )


def planned_future_expenses_cents(input_data: PaceInput) -> int:
    return sum(
        expense.amount_cents
        * len(
            future_occurrence_dates(
                next_date=expense.next_date,
                frequency=expense.frequency,
                calculated_at=input_data.calculated_at,
                user_time_zone=input_data.user_time_zone,
                target_date=input_data.target_date,
            )
        )
        for expense in input_data.planned_expenses
        if expense.active
    )


def forecast_resources_cents(
    *,
    current_cash_cents: int,
    confirmed_future_income_cents: int,
    planned_future_expenses_cents: int,
    reserve_buffer_cents: int,
) -> int:
    return (
        current_cash_cents
        + confirmed_future_income_cents
        - planned_future_expenses_cents
        - reserve_buffer_cents
    )


def goal_gap_cents(*, target_cents: int, current_saved_cents: int) -> int:
    return max(0, target_cents - current_saved_cents)


def discretionary_capacity_cents(*, forecast_resources_cents: int, goal_gap_cents: int) -> int:
    return forecast_resources_cents - goal_gap_cents


def remaining_weeks(calculated_at: datetime, user_time_zone: str, target_date: date) -> int:
    days_remaining = (target_date - calculation_local_date(calculated_at, user_time_zone)).days
    return max(1, _ceil_div(days_remaining, 7))


def weekly_safe_to_spend_cents(discretionary_capacity_cents: int, remaining_weeks: int) -> int:
    if remaining_weeks < 1:
        raise ValueError("remaining_weeks must be at least 1")
    weekly_capacity_cents = discretionary_capacity_cents // remaining_weeks
    return max(0, (weekly_capacity_cents // 100) * 100)


def projected_shortfall_cents(*, goal_gap_cents: int, forecast_resources_cents: int) -> int:
    return max(0, goal_gap_cents - forecast_resources_cents)


def suggest_reserve_buffer_cents(confirmed_future_income_cents: int) -> int:
    if confirmed_future_income_cents < 0:
        raise ValueError("confirmed_future_income_cents must be non-negative")
    return _ceil_div(confirmed_future_income_cents, 2_000) * 100


# Pace status helpers


def expected_savings_to_date_cents(
    *,
    initial_saved_cents: int,
    target_cents: int,
    start_date: date,
    target_date: date,
    calculated_at: datetime,
    user_time_zone: str,
) -> int:
    total_days = (target_date - start_date).days
    if total_days <= 0:
        return target_cents

    elapsed_days = (calculation_local_date(calculated_at, user_time_zone) - start_date).days
    clamped_elapsed_days = min(max(elapsed_days, 0), total_days)
    savings_delta_cents = target_cents - initial_saved_cents
    return initial_saved_cents + (savings_delta_cents * clamped_elapsed_days) // total_days


def pace_tolerance_cents(target_cents: int) -> int:
    if target_cents <= 0:
        raise ValueError("target_cents must be positive")
    return max(2_500, target_cents // 20)


def evaluate_pace_status(
    *,
    goal_gap_cents: int,
    forecast_resources_cents: int,
    current_saved_cents: int,
    expected_savings_to_date_cents: int,
    tolerance_cents: int,
) -> PaceStatus:
    if goal_gap_cents == 0:
        return PaceStatus.COMPLETED
    if forecast_resources_cents < goal_gap_cents:
        return PaceStatus.OFF_PACE
    if current_saved_cents - expected_savings_to_date_cents >= tolerance_cents:
        return PaceStatus.AHEAD
    if expected_savings_to_date_cents - current_saved_cents >= tolerance_cents:
        return PaceStatus.AT_RISK
    return PaceStatus.ON_TRACK


# Internal helpers


def _expand_occurrences(
    next_date: date, frequency: RecurrenceFrequency, target_date: date
) -> tuple[date, ...]:
    if next_date > target_date:
        return ()

    occurrences: list[date] = []
    occurrence_date = next_date
    original_day = next_date.day

    while occurrence_date <= target_date:
        occurrences.append(occurrence_date)
        if frequency is RecurrenceFrequency.ONE_TIME:
            break
        if frequency is RecurrenceFrequency.WEEKLY:
            occurrence_date += timedelta(days=7)
        elif frequency is RecurrenceFrequency.BIWEEKLY:
            occurrence_date += timedelta(days=14)
        elif frequency is RecurrenceFrequency.MONTHLY:
            occurrence_date = _add_one_month(occurrence_date, original_day)

    return tuple(occurrences)


def _add_one_month(value: date, original_day: int) -> date:
    next_month = value.month + 1
    next_year = value.year
    if next_month == 13:
        next_month = 1
        next_year += 1
    day = min(original_day, monthrange(next_year, next_month)[1])
    return date(next_year, next_month, day)


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)
