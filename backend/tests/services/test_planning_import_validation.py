from datetime import date

import pytest
from app.services.planning_import import PlanningImport
from app.services.planning_import_parser import parse_planning_csv
from app.services.planning_import_validation import (
    PlanningCsvValidationError,
    validate_planning_csv,
)

HEADER = (
    "record_type,name,target_amount,initial_saved,current_saved,starting_cash,"
    "balance_date,reserve_buffer,amount,date,frequency,confidence,classification,"
    "start_date,target_date"
)
GOAL = "goal,Moving fund,3000.00,500.00,1125.00,,,,,,,,,2026-08-01,2026-11-15"
CASH = "cash,,,,,2000.00,2026-08-26,300.00,,,,,,,"


def _parse(data_rows: str):
    return parse_planning_csv(f"{HEADER}\n{data_rows}\n")


def test_validates_and_normalizes_a_complete_plan() -> None:
    parsed = _parse(
        "\n".join(
            [
                GOAL,
                CASH,
                "income,Salary,,,,,,,2500.00,2026-09-01,biweekly,confirmed,,,",
                "expense,Rent,,,,,,,1400.00,2026-09-01,monthly,,essential,,",
            ]
        )
    )

    planning_import = validate_planning_csv(parsed, user_local_date=date(2026, 8, 27))

    assert isinstance(planning_import, PlanningImport)
    assert planning_import.goal.target_cents == 300_000
    assert planning_import.cash.starting_cash_cents == 200_000
    assert planning_import.income_sources[0].amount_cents == 250_000
    assert planning_import.planned_expenses[0].classification.value == "essential"


def test_validates_a_minimal_plan_without_income_or_expenses() -> None:
    planning_import = validate_planning_csv(
        _parse(f"{GOAL}\n{CASH}"),
        user_local_date=date(2026, 8, 27),
    )

    assert planning_import.income_sources == ()
    assert planning_import.planned_expenses == ()


def test_reports_missing_and_unknown_headers() -> None:
    parsed = parse_planning_csv(
        "record_type,name,target_amount,unexpected\ngoal,Goal,3000.00,value\n"
    )

    with pytest.raises(PlanningCsvValidationError) as exc_info:
        validate_planning_csv(parsed, user_local_date=date(2026, 8, 27))

    issues = {(issue.field, issue.code) for issue in exc_info.value.issues}
    assert ("unexpected", "unknown_header") in issues
    assert ("initial_saved", "missing_header") in issues


def test_reports_row_and_cross_row_errors() -> None:
    parsed = _parse(
        "\n".join(
            [
                "goal,Goal,10.00,-1,20,,,,,,,,,2026-08-28,2026-08-27",
                "cash,,,,,100.00,2026-08-28,5.00,,,,,,,",
                "income,Salary,,,,,,,0.001,2026-02-30,yearly,maybe,,,",
            ]
        )
    )

    with pytest.raises(PlanningCsvValidationError) as exc_info:
        validate_planning_csv(parsed, user_local_date=date(2026, 8, 27))

    issues = {(issue.row, issue.field, issue.code) for issue in exc_info.value.issues}
    assert (2, "initial_saved", "invalid_money") in issues
    assert (2, "current_saved", "exceeds_target") in issues
    assert (2, "start_date", "invalid_date_range") in issues
    assert (2, "target_date", "target_date_not_future") in issues
    assert (3, "balance_date", "balance_date_in_future") in issues
    assert (4, "amount", "invalid_money") in issues
    assert (4, "date", "invalid_date") in issues
    assert (4, "frequency", "invalid_enum") in issues
    assert (4, "confidence", "invalid_enum") in issues


def test_rejects_duplicate_singleton_rows() -> None:
    with pytest.raises(PlanningCsvValidationError) as exc_info:
        validate_planning_csv(
            _parse(f"{GOAL}\n{GOAL}\n{CASH}\n{CASH}"),
            user_local_date=date(2026, 8, 27),
        )

    codes = [issue.code for issue in exc_info.value.issues]
    assert "duplicate_goal" in codes
    assert "duplicate_cash" in codes


def test_rejects_populated_fields_that_do_not_apply_to_a_row() -> None:
    with pytest.raises(PlanningCsvValidationError) as exc_info:
        validate_planning_csv(
            _parse(
                "\n".join(
                    [
                        GOAL,
                        "cash,,,,,2000.00,2026-08-26,300.00,1.00,,,,,,",
                    ]
                )
            ),
            user_local_date=date(2026, 8, 27),
        )

    assert any(
        issue.field == "amount" and issue.code == "inapplicable_field"
        for issue in exc_info.value.issues
    )
