from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any

FORMULA_VERSION = "pace-v1"


class GoalStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PaceStatus(StrEnum):
    COMPLETED = "Completed"
    OFF_PACE = "Off Pace"
    AHEAD = "Ahead"
    AT_RISK = "At Risk"
    ON_TRACK = "On Track"


class IncomeConfidence(StrEnum):
    CONFIRMED = "confirmed"
    UNCONFIRMED = "unconfirmed"


class ExpenseClassification(StrEnum):
    ESSENTIAL = "essential"
    DISCRETIONARY = "discretionary"


class RecurrenceFrequency(StrEnum):
    ONE_TIME = "one_time"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


def _require_int_cents(name: str, value: int) -> None:
    if not isinstance(value, int):
        raise TypeError(f"{name} must be integer cents")


def _require_non_negative_cents(name: str, value: int) -> None:
    _require_int_cents(name, value)
    if value < 0:
        raise ValueError(f"{name} must be non-negative")


def _require_positive_cents(name: str, value: int) -> None:
    _require_int_cents(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _require_timezone_aware(name: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


def _freeze_metadata(metadata: dict[str, Any]) -> MappingProxyType[str, Any]:
    return MappingProxyType(dict(metadata))


@dataclass(frozen=True, slots=True)
class IncomeSourceInput:
    name: str
    amount_cents: int
    next_date: date
    frequency: RecurrenceFrequency
    confidence: IncomeConfidence
    active: bool = True

    def __post_init__(self) -> None:
        _require_non_negative_cents("amount_cents", self.amount_cents)


@dataclass(frozen=True, slots=True)
class PlannedExpenseInput:
    name: str
    amount_cents: int
    next_date: date
    frequency: RecurrenceFrequency
    classification: ExpenseClassification
    active: bool = True

    def __post_init__(self) -> None:
        _require_non_negative_cents("amount_cents", self.amount_cents)


@dataclass(frozen=True, slots=True)
class PaceInput:
    formula_version: str
    calculated_at: datetime
    user_time_zone: str
    target_cents: int
    initial_saved_cents: int
    current_saved_cents: int
    start_date: date
    target_date: date
    starting_cash_cents: int
    balance_as_of_date: date
    reserve_buffer_cents: int
    income_sources: tuple[IncomeSourceInput, ...] = field(default_factory=tuple)
    planned_expenses: tuple[PlannedExpenseInput, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.formula_version != FORMULA_VERSION:
            raise ValueError(f"formula_version must be {FORMULA_VERSION}")
        _require_timezone_aware("calculated_at", self.calculated_at)
        _require_positive_cents("target_cents", self.target_cents)
        _require_non_negative_cents("initial_saved_cents", self.initial_saved_cents)
        _require_non_negative_cents("current_saved_cents", self.current_saved_cents)
        _require_non_negative_cents("starting_cash_cents", self.starting_cash_cents)
        _require_non_negative_cents("reserve_buffer_cents", self.reserve_buffer_cents)
        if self.initial_saved_cents > self.target_cents:
            raise ValueError("initial_saved_cents cannot exceed target_cents")
        if self.target_date < self.start_date:
            raise ValueError("target_date cannot be before start_date")
        object.__setattr__(self, "income_sources", tuple(self.income_sources))
        object.__setattr__(self, "planned_expenses", tuple(self.planned_expenses))


@dataclass(frozen=True, slots=True)
class PaceResult:
    formula_version: str
    current_cash_cents: int
    confirmed_future_income_cents: int
    planned_future_expenses_cents: int
    reserve_buffer_cents: int
    forecast_resources_cents: int
    goal_gap_cents: int
    discretionary_capacity_cents: int
    remaining_weeks: int
    weekly_safe_to_spend_cents: int
    projected_shortfall_cents: int
    expected_savings_to_date_cents: int
    pace_status: PaceStatus
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        if self.formula_version != FORMULA_VERSION:
            raise ValueError(f"formula_version must be {FORMULA_VERSION}")
        _require_int_cents("current_cash_cents", self.current_cash_cents)
        _require_non_negative_cents(
            "confirmed_future_income_cents", self.confirmed_future_income_cents
        )
        _require_non_negative_cents(
            "planned_future_expenses_cents", self.planned_future_expenses_cents
        )
        _require_non_negative_cents("reserve_buffer_cents", self.reserve_buffer_cents)
        _require_int_cents("forecast_resources_cents", self.forecast_resources_cents)
        _require_non_negative_cents("goal_gap_cents", self.goal_gap_cents)
        _require_int_cents("discretionary_capacity_cents", self.discretionary_capacity_cents)
        if self.remaining_weeks < 1:
            raise ValueError("remaining_weeks must be at least 1")
        _require_non_negative_cents(
            "weekly_safe_to_spend_cents", self.weekly_safe_to_spend_cents
        )
        _require_non_negative_cents("projected_shortfall_cents", self.projected_shortfall_cents)
        _require_non_negative_cents(
            "expected_savings_to_date_cents", self.expected_savings_to_date_cents
        )
        object.__setattr__(self, "metadata", _freeze_metadata(dict(self.metadata)))
