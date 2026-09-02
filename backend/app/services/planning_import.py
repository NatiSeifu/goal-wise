"""Typed domain objects for a canonical planning import."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.pace_engine.types import IncomeSourceInput, PlannedExpenseInput


@dataclass(frozen=True, slots=True)
class PlanningImportGoal:
    """Normalized goal values supplied by an import document."""

    name: str
    target_cents: int
    initial_saved_cents: int
    current_saved_cents: int
    start_date: date
    target_date: date


@dataclass(frozen=True, slots=True)
class PlanningImportCash:
    """Normalized cash and reserve values supplied by an import document."""

    starting_cash_cents: int
    balance_as_of_date: date
    reserve_buffer_cents: int


@dataclass(frozen=True, slots=True)
class PlanningImport:
    """One complete, normalized planning setup ready for later validation."""

    goal: PlanningImportGoal
    cash: PlanningImportCash
    income_sources: tuple[IncomeSourceInput, ...] = field(default_factory=tuple)
    planned_expenses: tuple[PlannedExpenseInput, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "income_sources", tuple(self.income_sources))
        object.__setattr__(self, "planned_expenses", tuple(self.planned_expenses))
