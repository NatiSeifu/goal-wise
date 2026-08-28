"""Planning CSV preview API schemas."""

from datetime import date

from pydantic import BaseModel


class PlanningImportIssueResponse(BaseModel):
    row: int
    field: str
    code: str
    message: str


class PlanningImportGoalPreview(BaseModel):
    name: str
    target_cents: int
    initial_saved_cents: int
    current_saved_cents: int
    start_date: date
    target_date: date


class PlanningImportCashPreview(BaseModel):
    starting_cash_cents: int
    balance_as_of_date: date
    reserve_buffer_cents: int


class PlanningImportSourcePreview(BaseModel):
    name: str
    amount_cents: int
    next_date: date
    frequency: str
    confidence: str | None = None
    classification: str | None = None


class PlanningImportPreviewResponse(BaseModel):
    valid: bool
    row_count: int
    counts: dict[str, int]
    goal: PlanningImportGoalPreview
    cash: PlanningImportCashPreview
    income_sources: list[PlanningImportSourcePreview]
    planned_expenses: list[PlanningImportSourcePreview]
    errors: list[PlanningImportIssueResponse]
