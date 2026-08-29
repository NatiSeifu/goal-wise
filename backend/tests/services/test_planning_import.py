from datetime import date

from app.pace_engine import (
    ExpenseClassification,
    IncomeConfidence,
    IncomeSourceInput,
    PlannedExpenseInput,
    RecurrenceFrequency,
)
from app.services.planning_import import (
    PlanningImport,
    PlanningImportCash,
    PlanningImportGoal,
)


def test_planning_import_represents_a_complete_normalized_plan() -> None:
    planning_import = PlanningImport(
        goal=PlanningImportGoal(
            name="Moving fund",
            target_cents=300_000,
            initial_saved_cents=50_000,
            current_saved_cents=112_500,
            start_date=date(2026, 8, 1),
            target_date=date(2026, 11, 15),
        ),
        cash=PlanningImportCash(
            starting_cash_cents=200_000,
            balance_as_of_date=date(2026, 8, 26),
            reserve_buffer_cents=30_000,
        ),
        income_sources=(
            IncomeSourceInput(
                name="Salary",
                amount_cents=250_000,
                next_date=date(2026, 9, 1),
                frequency=RecurrenceFrequency.BIWEEKLY,
                confidence=IncomeConfidence.CONFIRMED,
            ),
        ),
        planned_expenses=(
            PlannedExpenseInput(
                name="Rent",
                amount_cents=140_000,
                next_date=date(2026, 9, 1),
                frequency=RecurrenceFrequency.MONTHLY,
                classification=ExpenseClassification.ESSENTIAL,
            ),
        ),
    )

    assert planning_import.goal.name == "Moving fund"
    assert planning_import.goal.current_saved_cents == 112_500
    assert planning_import.cash.starting_cash_cents == 200_000
    assert planning_import.income_sources[0].confidence is IncomeConfidence.CONFIRMED
    assert planning_import.planned_expenses[0].classification is ExpenseClassification.ESSENTIAL


def test_planning_import_supports_a_minimal_plan_without_sources() -> None:
    planning_import = PlanningImport(
        goal=PlanningImportGoal(
            name="Emergency fund",
            target_cents=100_000,
            initial_saved_cents=0,
            current_saved_cents=0,
            start_date=date(2026, 8, 1),
            target_date=date(2026, 12, 31),
        ),
        cash=PlanningImportCash(
            starting_cash_cents=50_000,
            balance_as_of_date=date(2026, 8, 26),
            reserve_buffer_cents=5_000,
        ),
    )

    assert planning_import.income_sources == ()
    assert planning_import.planned_expenses == ()


def test_planning_import_freezes_source_collections_as_tuples() -> None:
    income_sources = [
        IncomeSourceInput(
            name="Salary",
            amount_cents=250_000,
            next_date=date(2026, 9, 1),
            frequency=RecurrenceFrequency.MONTHLY,
            confidence=IncomeConfidence.CONFIRMED,
        ),
    ]
    planning_import = PlanningImport(
        goal=PlanningImportGoal(
            name="Emergency fund",
            target_cents=100_000,
            initial_saved_cents=0,
            current_saved_cents=0,
            start_date=date(2026, 8, 1),
            target_date=date(2026, 12, 31),
        ),
        cash=PlanningImportCash(
            starting_cash_cents=50_000,
            balance_as_of_date=date(2026, 8, 26),
            reserve_buffer_cents=5_000,
        ),
        income_sources=income_sources,
    )

    income_sources.append(
        IncomeSourceInput(
            name="Bonus",
            amount_cents=10_000,
            next_date=date(2026, 10, 1),
            frequency=RecurrenceFrequency.ONE_TIME,
            confidence=IncomeConfidence.UNCONFIRMED,
        ),
    )

    assert len(planning_import.income_sources) == 1
