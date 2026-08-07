from __future__ import annotations

import ast
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from app.pace_engine import (
    FORMULA_VERSION,
    ExpenseClassification,
    GoalStatus,
    IncomeConfidence,
    IncomeSourceInput,
    PaceInput,
    PaceResult,
    PaceStatus,
    PlannedExpenseInput,
    RecurrenceFrequency,
)


def test_exports_formula_version_and_status_values() -> None:
    assert FORMULA_VERSION == "pace-v1"
    assert [status.value for status in GoalStatus] == ["active", "completed", "archived"]
    assert [status.value for status in PaceStatus] == [
        "Completed",
        "Off Pace",
        "Ahead",
        "At Risk",
        "On Track",
    ]


def test_constructs_valid_pace_input() -> None:
    input_data = PaceInput(
        formula_version=FORMULA_VERSION,
        calculated_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        user_time_zone="America/Los_Angeles",
        target_cents=100_000,
        initial_saved_cents=10_000,
        current_saved_cents=25_000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        starting_cash_cents=50_000,
        balance_as_of_date=date(2026, 8, 6),
        reserve_buffer_cents=5_000,
        income_sources=(
            IncomeSourceInput(
                name="Paycheck",
                amount_cents=100_000,
                next_date=date(2026, 8, 14),
                frequency=RecurrenceFrequency.BIWEEKLY,
                confidence=IncomeConfidence.CONFIRMED,
            ),
        ),
        planned_expenses=(
            PlannedExpenseInput(
                name="Rent",
                amount_cents=150_000,
                next_date=date(2026, 9, 1),
                frequency=RecurrenceFrequency.MONTHLY,
                classification=ExpenseClassification.ESSENTIAL,
            ),
        ),
    )

    assert input_data.formula_version == FORMULA_VERSION
    assert input_data.income_sources[0].confidence is IncomeConfidence.CONFIRMED
    assert input_data.planned_expenses[0].classification is ExpenseClassification.ESSENTIAL


def test_rejects_naive_calculation_timestamp() -> None:
    with pytest.raises(ValueError, match="calculated_at must be timezone-aware"):
        PaceInput(
            formula_version=FORMULA_VERSION,
            calculated_at=datetime(2026, 8, 7, 12, 0),
            user_time_zone="America/Los_Angeles",
            target_cents=100_000,
            initial_saved_cents=0,
            current_saved_cents=0,
            start_date=date(2026, 8, 1),
            target_date=date(2026, 12, 31),
            starting_cash_cents=50_000,
            balance_as_of_date=date(2026, 8, 6),
            reserve_buffer_cents=5_000,
        )


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("target_cents", 0, "target_cents must be positive"),
        ("initial_saved_cents", -1, "initial_saved_cents must be non-negative"),
        ("current_saved_cents", -1, "current_saved_cents must be non-negative"),
        ("starting_cash_cents", -1, "starting_cash_cents must be non-negative"),
        ("reserve_buffer_cents", -1, "reserve_buffer_cents must be non-negative"),
    ],
)
def test_rejects_invalid_input_money_fields(field_name: str, value: int, message: str) -> None:
    kwargs = {
        "formula_version": FORMULA_VERSION,
        "calculated_at": datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        "user_time_zone": "America/Los_Angeles",
        "target_cents": 100_000,
        "initial_saved_cents": 0,
        "current_saved_cents": 0,
        "start_date": date(2026, 8, 1),
        "target_date": date(2026, 12, 31),
        "starting_cash_cents": 50_000,
        "balance_as_of_date": date(2026, 8, 6),
        "reserve_buffer_cents": 5_000,
        field_name: value,
    }

    with pytest.raises(ValueError, match=message):
        PaceInput(**kwargs)


def test_allows_current_saved_amount_above_target_for_completed_goals() -> None:
    input_data = PaceInput(
        formula_version=FORMULA_VERSION,
        calculated_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
        user_time_zone="America/Los_Angeles",
        target_cents=100_000,
        initial_saved_cents=0,
        current_saved_cents=100_001,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        starting_cash_cents=50_000,
        balance_as_of_date=date(2026, 8, 6),
        reserve_buffer_cents=5_000,
    )

    assert input_data.current_saved_cents == 100_001


def test_rejects_initial_saved_amount_above_target() -> None:
    with pytest.raises(ValueError, match="initial_saved_cents cannot exceed target_cents"):
        PaceInput(
            formula_version=FORMULA_VERSION,
            calculated_at=datetime(2026, 8, 7, 12, 0, tzinfo=UTC),
            user_time_zone="America/Los_Angeles",
            target_cents=100_000,
            initial_saved_cents=100_001,
            current_saved_cents=0,
            start_date=date(2026, 8, 1),
            target_date=date(2026, 12, 31),
            starting_cash_cents=50_000,
            balance_as_of_date=date(2026, 8, 6),
            reserve_buffer_cents=5_000,
        )


def test_constructs_result_with_required_outputs() -> None:
    result = PaceResult(
        formula_version=FORMULA_VERSION,
        current_cash_cents=50_000,
        confirmed_future_income_cents=200_000,
        planned_future_expenses_cents=100_000,
        reserve_buffer_cents=5_000,
        forecast_resources_cents=145_000,
        goal_gap_cents=75_000,
        discretionary_capacity_cents=70_000,
        remaining_weeks=10,
        weekly_safe_to_spend_cents=7_000,
        projected_shortfall_cents=0,
        expected_savings_to_date_cents=20_000,
        pace_status=PaceStatus.ON_TRACK,
        metadata={"scenario": "contract"},
    )

    assert result.pace_status is PaceStatus.ON_TRACK
    assert result.metadata["scenario"] == "contract"
    with pytest.raises(TypeError):
        result.metadata["scenario"] = "changed"


def test_rejects_invalid_result_values() -> None:
    with pytest.raises(ValueError, match="remaining_weeks must be at least 1"):
        PaceResult(
            formula_version=FORMULA_VERSION,
            current_cash_cents=50_000,
            confirmed_future_income_cents=200_000,
            planned_future_expenses_cents=100_000,
            reserve_buffer_cents=5_000,
            forecast_resources_cents=145_000,
            goal_gap_cents=75_000,
            discretionary_capacity_cents=70_000,
            remaining_weeks=0,
            weekly_safe_to_spend_cents=7_000,
            projected_shortfall_cents=0,
            expected_savings_to_date_cents=20_000,
            pace_status=PaceStatus.ON_TRACK,
        )


def test_pace_engine_has_no_forbidden_dependencies() -> None:
    forbidden_imports = {
        "fastapi",
        "sqlalchemy",
        "app.api",
        "app.db",
        "app.models",
        "app.repositories",
        "app.services",
    }
    package_dir = Path(__file__).parents[2] / "app" / "pace_engine"

    imported_modules: set[str] = set()
    for source_file in package_dir.glob("*.py"):
        tree = ast.parse(source_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_modules.add(node.module)

    assert imported_modules.isdisjoint(forbidden_imports)
