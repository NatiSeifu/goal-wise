"""Versioned contracts for immutable calculation snapshot documents."""

from collections.abc import Mapping
from datetime import date, datetime
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    ValidationError,
)

SnapshotInputSchemaVersion = Literal["snapshot-input-v1"]
SnapshotResultSchemaVersion = Literal["snapshot-result-v1"]
FormulaVersion = Literal["pace-v1"]
GoalStatus = Literal["active", "completed", "archived"]
PaceStatus = Literal["Completed", "Off Pace", "Ahead", "At Risk", "On Track"]
RecurrenceFrequency = Literal["one_time", "weekly", "biweekly", "monthly"]
IncomeConfidence = Literal["confirmed", "unconfirmed"]
ExpenseClassification = Literal["essential", "discretionary"]
TransactionCategory = str
TransactionSource = str
DuplicateStatus = str
ChangedInputCategory = Literal[
    "goal",
    "financial_profile",
    "income_sources",
    "planned_expenses",
    "transactions",
]

SignedCents = StrictInt
NonNegativeCents = Annotated[StrictInt, Field(ge=0)]
Percentage = Annotated[StrictFloat, Field(ge=0, le=100)]


class SnapshotModel(BaseModel):
    """Common strict configuration for persisted snapshot documents."""

    model_config = ConfigDict(extra="forbid")


class SnapshotContractError(ValueError):
    """Raised when persisted snapshot JSON is not a supported document."""


class SnapshotCalculationV1(SnapshotModel):
    timestamp_utc: datetime
    user_time_zone: str = Field(min_length=1)
    trigger: str = Field(min_length=1)


class SnapshotGoalV1(SnapshotModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    target_cents: NonNegativeCents
    initial_saved_cents: NonNegativeCents
    current_saved_cents: NonNegativeCents
    start_date: date
    target_date: date
    status: GoalStatus


class SnapshotFinancialProfileV1(SnapshotModel):
    starting_cash_cents: NonNegativeCents
    balance_as_of_date: date
    reserve_buffer_cents: NonNegativeCents
    reserve_buffer_confirmed: StrictBool


class SnapshotIncomeSourceV1(SnapshotModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    amount_cents: NonNegativeCents
    next_date: date
    frequency: RecurrenceFrequency
    confidence: IncomeConfidence
    active: StrictBool


class SnapshotPlannedExpenseV1(SnapshotModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    amount_cents: NonNegativeCents
    next_date: date
    frequency: RecurrenceFrequency
    classification: ExpenseClassification
    active: StrictBool


class SnapshotTransactionV1(SnapshotModel):
    """Allowed transaction facts for future snapshot transaction support."""

    id: str = Field(min_length=1)
    date: date
    amount_cents: StrictInt
    category: TransactionCategory = Field(min_length=1)
    source: TransactionSource = Field(min_length=1)
    duplicate_status: DuplicateStatus = Field(min_length=1)
    included_in_current_cash: StrictBool


class SnapshotInputV1(SnapshotModel):
    schema_version: SnapshotInputSchemaVersion
    formula_version: FormulaVersion
    calculation: SnapshotCalculationV1
    goal: SnapshotGoalV1
    financial_profile: SnapshotFinancialProfileV1
    income_sources: list[SnapshotIncomeSourceV1]
    planned_expenses: list[SnapshotPlannedExpenseV1]
    transactions: list[SnapshotTransactionV1]


class SnapshotOutputsV1(SnapshotModel):
    current_cash_cents: SignedCents
    confirmed_future_income_cents: NonNegativeCents
    planned_future_expenses_cents: NonNegativeCents
    reserve_buffer_cents: NonNegativeCents
    forecast_resources_cents: SignedCents
    goal_gap_cents: NonNegativeCents
    discretionary_capacity_cents: SignedCents
    remaining_weeks: Annotated[StrictInt, Field(ge=1)]
    weekly_safe_to_spend_cents: NonNegativeCents
    projected_shortfall_cents: NonNegativeCents
    expected_savings_to_date_cents: NonNegativeCents
    pace_status: PaceStatus
    progress_percentage: Percentage
    current_week_opening_allowance_cents: NonNegativeCents
    current_week_remainder_cents: NonNegativeCents


class SnapshotExplanationSummaryV1(SnapshotModel):
    confirmed_income_count: Annotated[StrictInt, Field(ge=0)]
    planned_expense_count: Annotated[StrictInt, Field(ge=0)]
    unconfirmed_income_count: Annotated[StrictInt, Field(ge=0)]


class SnapshotExplanationV1(SnapshotModel):
    included_income_source_ids: list[str]
    excluded_income_source_ids: list[str]
    included_planned_expense_ids: list[str]
    excluded_planned_expense_ids: list[str]
    summary: SnapshotExplanationSummaryV1


class SnapshotChangedFromPreviousV1(SnapshotModel):
    previous_snapshot_id: str | None
    changed_input_categories: list[ChangedInputCategory]
    weekly_safe_to_spend_delta_cents: SignedCents | None


class SnapshotResultV1(SnapshotModel):
    schema_version: SnapshotResultSchemaVersion
    formula_version: FormulaVersion
    outputs: SnapshotOutputsV1
    explanation: SnapshotExplanationV1
    changed_from_previous: SnapshotChangedFromPreviousV1


def parse_snapshot_input(document: Mapping[str, Any]) -> SnapshotInputV1:
    """Parse a persisted input document through the active version boundary."""

    try:
        return SnapshotInputV1.model_validate(document)
    except ValidationError as exc:
        raise SnapshotContractError("Snapshot input failed contract validation.") from exc


def parse_snapshot_result(document: Mapping[str, Any]) -> SnapshotResultV1:
    """Parse a persisted result document through the active version boundary."""

    try:
        return SnapshotResultV1.model_validate(document)
    except ValidationError as exc:
        raise SnapshotContractError("Snapshot result failed contract validation.") from exc
