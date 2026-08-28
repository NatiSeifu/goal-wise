"""Domain validation and normalization for canonical planning CSV records."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import cast

from app.pace_engine import (
    ExpenseClassification,
    IncomeConfidence,
    IncomeSourceInput,
    PlannedExpenseInput,
    RecurrenceFrequency,
)
from app.services.planning_import import PlanningImport, PlanningImportCash, PlanningImportGoal
from app.services.planning_import_parser import ParsedPlanningCsv

CANONICAL_PLANNING_CSV_HEADERS = (
    "record_type",
    "name",
    "target_amount",
    "initial_saved",
    "current_saved",
    "starting_cash",
    "balance_date",
    "reserve_buffer",
    "amount",
    "date",
    "frequency",
    "confidence",
    "classification",
    "start_date",
    "target_date",
)
MAX_PLANNING_IMPORT_ERRORS = 100
MAX_PLANNING_IMPORT_FIELD_LENGTH = 500
_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_MONEY_PATTERN = re.compile(r"^\d+(?:\.\d{1,2})?$")


@dataclass(frozen=True, slots=True)
class PlanningCsvValidationIssue:
    """One user-correctable validation issue."""

    row: int
    field: str
    code: str
    message: str


class PlanningCsvValidationError(ValueError):
    """Raised when a parsed planning CSV violates the domain contract."""

    def __init__(self, issues: tuple[PlanningCsvValidationIssue, ...]) -> None:
        self.issues = issues
        super().__init__("Planning CSV validation failed.")


def validation_issue_dict(issue: PlanningCsvValidationIssue) -> dict[str, object]:
    """Return the stable public representation of a validation issue."""

    return {
        "row": issue.row,
        "field": issue.field,
        "code": issue.code,
        "message": issue.message,
    }


def validate_planning_csv(
    parsed: ParsedPlanningCsv,
    *,
    user_local_date: date,
) -> PlanningImport:
    """Validate and normalize parsed CSV records without persistence."""

    issues: list[PlanningCsvValidationIssue] = []
    _validate_headers(parsed, issues)
    if issues:
        raise PlanningCsvValidationError(tuple(issues))

    goal: PlanningImportGoal | None = None
    cash: PlanningImportCash | None = None
    goal_seen = False
    cash_seen = False
    income_sources: list[IncomeSourceInput] = []
    planned_expenses: list[PlannedExpenseInput] = []

    for row in parsed.rows:
        values = dict(zip(parsed.headers, row.values, strict=True))
        if any(len(value) > MAX_PLANNING_IMPORT_FIELD_LENGTH for value in values.values()):
            _add_issue(
                issues,
                row=row.row_number,
                field="document",
                code="field_length_exceeded",
                message=(
                    "Fields cannot contain more than "
                    f"{MAX_PLANNING_IMPORT_FIELD_LENGTH} characters."
                ),
            )
            continue

        record_type = values["record_type"].strip()
        if record_type not in {"goal", "cash", "income", "expense"}:
            _add_issue(
                issues,
                row=row.row_number,
                field="record_type",
                code="unsupported_record_type",
                message="Must be one of: goal, cash, income, expense.",
            )
            continue

        _validate_applicable_fields(values, record_type, row.row_number, issues)
        if record_type == "goal":
            duplicate_goal = goal_seen
            goal_seen = True
            parsed_goal = _goal_from_row(values, row.row_number, user_local_date, issues)
            if parsed_goal is not None:
                if duplicate_goal:
                    _add_issue(
                        issues,
                        row=row.row_number,
                        field="record_type",
                        code="duplicate_goal",
                        message="The document must contain exactly one goal row.",
                    )
                else:
                    goal = parsed_goal
        elif record_type == "cash":
            duplicate_cash = cash_seen
            cash_seen = True
            parsed_cash = _cash_from_row(values, row.row_number, user_local_date, issues)
            if parsed_cash is not None:
                if duplicate_cash:
                    _add_issue(
                        issues,
                        row=row.row_number,
                        field="record_type",
                        code="duplicate_cash",
                        message="The document must contain exactly one cash row.",
                    )
                else:
                    cash = parsed_cash
        elif record_type == "income":
            parsed_income = _income_from_row(values, row.row_number, issues)
            if parsed_income is not None:
                income_sources.append(parsed_income)
        else:
            parsed_expense = _expense_from_row(values, row.row_number, issues)
            if parsed_expense is not None:
                planned_expenses.append(parsed_expense)

        if len(issues) >= MAX_PLANNING_IMPORT_ERRORS:
            break

    if not goal_seen:
        _add_issue(
            issues,
            row=1,
            field="document",
            code="missing_goal",
            message="The document must contain exactly one goal row.",
        )
    if not cash_seen:
        _add_issue(
            issues,
            row=1,
            field="document",
            code="missing_cash",
            message="The document must contain exactly one cash row.",
        )

    if issues:
        raise PlanningCsvValidationError(tuple(issues[:MAX_PLANNING_IMPORT_ERRORS]))
    assert goal is not None
    assert cash is not None
    return PlanningImport(
        goal=goal,
        cash=cash,
        income_sources=tuple(income_sources),
        planned_expenses=tuple(planned_expenses),
    )


def _validate_headers(
    parsed: ParsedPlanningCsv,
    issues: list[PlanningCsvValidationIssue],
) -> None:
    expected = set(CANONICAL_PLANNING_CSV_HEADERS)
    actual = set(parsed.headers)
    for header in parsed.headers:
        if header not in expected:
            _add_issue(
                issues,
                row=1,
                field=header or "document",
                code="unknown_header",
                message=f"Unknown column '{header}'.",
            )
    for header in CANONICAL_PLANNING_CSV_HEADERS:
        if header not in actual:
            _add_issue(
                issues,
                row=1,
                field=header,
                code="missing_header",
                message=f"Missing required column '{header}'.",
            )


def _validate_applicable_fields(
    values: dict[str, str],
    record_type: str,
    row_number: int,
    issues: list[PlanningCsvValidationIssue],
) -> None:
    applicable = {
        "goal": {
            "record_type",
            "name",
            "target_amount",
            "initial_saved",
            "current_saved",
            "start_date",
            "target_date",
        },
        "cash": {"record_type", "starting_cash", "balance_date", "reserve_buffer"},
        "income": {"record_type", "name", "amount", "date", "frequency", "confidence"},
        "expense": {"record_type", "name", "amount", "date", "frequency", "classification"},
    }[record_type]
    for field, value in values.items():
        if field not in applicable and value.strip():
            _add_issue(
                issues,
                row=row_number,
                field=field,
                code="inapplicable_field",
                message=f"'{field}' must be blank for a {record_type} row.",
            )


def _goal_from_row(
    values: dict[str, str],
    row_number: int,
    user_local_date: date,
    issues: list[PlanningCsvValidationIssue],
) -> PlanningImportGoal | None:
    name = _required_name(values["name"], row_number, "name", issues)
    target = _money(values["target_amount"], row_number, "target_amount", issues, positive=True)
    initial = _money(values["initial_saved"], row_number, "initial_saved", issues)
    current = _money(values["current_saved"], row_number, "current_saved", issues)
    start_date = _date(values["start_date"], row_number, "start_date", issues)
    target_date = _date(values["target_date"], row_number, "target_date", issues)
    if target is not None and target <= 0:
        _add_issue(
            issues,
            row=row_number,
            field="target_amount",
            code="not_positive",
            message="Must be greater than zero.",
        )
    if target is not None and initial is not None and initial > target:
        _add_issue(
            issues,
            row=row_number,
            field="initial_saved",
            code="exceeds_target",
            message="Cannot be greater than target_amount.",
        )
    if target is not None and current is not None and current > target:
        _add_issue(
            issues,
            row=row_number,
            field="current_saved",
            code="exceeds_target",
            message="Cannot be greater than target_amount.",
        )
    if start_date is not None and target_date is not None and start_date >= target_date:
        _add_issue(
            issues,
            row=row_number,
            field="start_date",
            code="invalid_date_range",
            message="Must be before target_date.",
        )
    if target_date is not None and target_date <= user_local_date:
        _add_issue(
            issues,
            row=row_number,
            field="target_date",
            code="target_date_not_future",
            message="Must be after the user's current local date.",
        )
    if None in (name, target, initial, current, start_date, target_date):
        return None
    assert name is not None
    assert target is not None
    assert initial is not None
    assert current is not None
    assert start_date is not None
    assert target_date is not None
    return PlanningImportGoal(name, target, initial, current, start_date, target_date)


def _cash_from_row(
    values: dict[str, str],
    row_number: int,
    user_local_date: date,
    issues: list[PlanningCsvValidationIssue],
) -> PlanningImportCash | None:
    starting_cash = _money(values["starting_cash"], row_number, "starting_cash", issues)
    balance_date = _date(values["balance_date"], row_number, "balance_date", issues)
    reserve_buffer = _money(values["reserve_buffer"], row_number, "reserve_buffer", issues)
    if balance_date is not None and balance_date > user_local_date:
        _add_issue(
            issues,
            row=row_number,
            field="balance_date",
            code="balance_date_in_future",
            message="Cannot be after the user's current local date.",
        )
    if None in (starting_cash, balance_date, reserve_buffer):
        return None
    assert starting_cash is not None
    assert balance_date is not None
    assert reserve_buffer is not None
    return PlanningImportCash(starting_cash, balance_date, reserve_buffer)


def _income_from_row(
    values: dict[str, str], row_number: int, issues: list[PlanningCsvValidationIssue]
) -> IncomeSourceInput | None:
    name = _required_name(values["name"], row_number, "name", issues)
    amount = _money(values["amount"], row_number, "amount", issues, positive=True)
    next_date = _date(values["date"], row_number, "date", issues)
    frequency = _enum(values["frequency"], RecurrenceFrequency, row_number, "frequency", issues)
    confidence = _enum(values["confidence"], IncomeConfidence, row_number, "confidence", issues)
    if None in (name, amount, next_date, frequency, confidence):
        return None
    assert name is not None
    assert amount is not None
    assert next_date is not None
    return IncomeSourceInput(
        name,
        amount,
        next_date,
        cast(RecurrenceFrequency, frequency),
        cast(IncomeConfidence, confidence),
    )


def _expense_from_row(
    values: dict[str, str], row_number: int, issues: list[PlanningCsvValidationIssue]
) -> PlannedExpenseInput | None:
    name = _required_name(values["name"], row_number, "name", issues)
    amount = _money(values["amount"], row_number, "amount", issues, positive=True)
    next_date = _date(values["date"], row_number, "date", issues)
    frequency = _enum(values["frequency"], RecurrenceFrequency, row_number, "frequency", issues)
    classification = _enum(
        values["classification"], ExpenseClassification, row_number, "classification", issues
    )
    if None in (name, amount, next_date, frequency, classification):
        return None
    assert name is not None
    assert amount is not None
    assert next_date is not None
    return PlannedExpenseInput(
        name,
        amount,
        next_date,
        cast(RecurrenceFrequency, frequency),
        cast(ExpenseClassification, classification),
    )


def _required_name(
    value: str, row: int, field: str, issues: list[PlanningCsvValidationIssue]
) -> str | None:
    normalized = value.strip()
    if not normalized:
        _add_issue(issues, row=row, field=field, code="required", message="Must not be blank.")
        return None
    return normalized


def _money(
    value: str,
    row: int,
    field: str,
    issues: list[PlanningCsvValidationIssue],
    *,
    positive: bool = False,
) -> int | None:
    normalized = value.strip()
    if not _MONEY_PATTERN.fullmatch(normalized):
        _add_issue(
            issues,
            row=row,
            field=field,
            code="invalid_money",
            message="Must be a nonnegative amount with at most two decimal places.",
        )
        return None
    try:
        cents = int(Decimal(normalized) * 100)
    except (InvalidOperation, ValueError):
        _add_issue(
            issues,
            row=row,
            field=field,
            code="invalid_money",
            message="Must be a valid decimal amount.",
        )
        return None
    if positive and cents <= 0:
        _add_issue(
            issues, row=row, field=field, code="not_positive", message="Must be greater than zero."
        )
        return None
    return cents


def _date(
    value: str, row: int, field: str, issues: list[PlanningCsvValidationIssue]
) -> date | None:
    normalized = value.strip()
    if not _DATE_PATTERN.fullmatch(normalized):
        _add_issue(
            issues, row=row, field=field, code="invalid_date", message="Must use YYYY-MM-DD."
        )
        return None
    try:
        return date.fromisoformat(normalized)
    except ValueError:
        _add_issue(
            issues,
            row=row,
            field=field,
            code="invalid_date",
            message="Must be a real calendar date in YYYY-MM-DD format.",
        )
        return None


def _enum(
    value: str,
    enum_type: type[RecurrenceFrequency] | type[IncomeConfidence] | type[ExpenseClassification],
    row: int,
    field: str,
    issues: list[PlanningCsvValidationIssue],
) -> RecurrenceFrequency | IncomeConfidence | ExpenseClassification | None:
    normalized = value.strip()
    try:
        return enum_type(normalized)
    except ValueError:
        allowed = ", ".join(member.value for member in enum_type)
        _add_issue(
            issues, row=row, field=field, code="invalid_enum", message=f"Must be one of: {allowed}."
        )
        return None


def _add_issue(
    issues: list[PlanningCsvValidationIssue],
    *,
    row: int,
    field: str,
    code: str,
    message: str,
) -> None:
    if len(issues) < MAX_PLANNING_IMPORT_ERRORS:
        issues.append(PlanningCsvValidationIssue(row, field, code, message))
