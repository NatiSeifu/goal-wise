"""Dashboard API schemas."""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel


class DashboardGoalSummary(BaseModel):
    id: str
    name: str
    target_cents: int
    current_saved_cents: int
    target_date: date


class DashboardPaceSummary(BaseModel):
    pace_status: str
    weekly_safe_to_spend_cents: int
    expected_savings_to_date_cents: int
    projected_shortfall_cents: int
    remaining_weeks: int
    progress_percentage: float
    current_week_opening_allowance_cents: int
    current_week_remainder_cents: int


class DashboardItem(BaseModel):
    status: str
    missing_inputs: list[str]
    snapshot_id: str | None
    calculated_at: datetime | None
    formula_version: str | None
    goal: DashboardGoalSummary | None
    pace: DashboardPaceSummary | None
    explanation: dict[str, Any] | None
    changed_from_previous: dict[str, Any] | None


class DashboardResponse(BaseModel):
    item: DashboardItem
