"""Dashboard API routes."""

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentSessionDep, DbSessionDep, NowDep
from app.models import CalculationSnapshot
from app.repositories.calculation_snapshots import get_latest_snapshot_for_user
from app.schemas.dashboard import (
    DashboardGoalSummary,
    DashboardItem,
    DashboardPaceSummary,
    DashboardResponse,
)
from app.services.auth import CurrentSession
from app.services.recalculation_boundary import (
    RecalculationStatus,
    prepare_pace_input_for_user,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

MISSING_SNAPSHOT = "calculation_snapshot"


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    current_session: CurrentSessionDep,
    db_session: DbSessionDep,
    now: NowDep,
) -> DashboardResponse:
    snapshot = get_latest_snapshot_for_user(
        db_session,
        user_id=current_session.user.id,
    )
    if snapshot is None:
        return DashboardResponse(
            item=_setup_required_dashboard_item(
                current_session=current_session,
                db_session=db_session,
                now=now,
            ),
        )

    return DashboardResponse(item=_ready_dashboard_item(snapshot))


def _setup_required_dashboard_item(
    *,
    current_session: CurrentSession,
    db_session: Session,
    now: datetime,
) -> DashboardItem:
    readiness = prepare_pace_input_for_user(
        db_session,
        user_id=current_session.user.id,
        user_time_zone=current_session.user.time_zone,
        calculated_at=now,
    )
    missing_inputs = [missing_input.value for missing_input in readiness.missing_inputs]
    if readiness.status is RecalculationStatus.READY:
        missing_inputs = [MISSING_SNAPSHOT]

    return DashboardItem(
        status="setup_required",
        missing_inputs=missing_inputs,
        snapshot_id=None,
        calculated_at=None,
        formula_version=None,
        goal=None,
        pace=None,
        explanation=None,
        changed_from_previous=None,
    )


def _ready_dashboard_item(snapshot: CalculationSnapshot) -> DashboardItem:
    result_json = snapshot.result_json
    normalized_input_json = snapshot.normalized_input_json
    outputs = _dict_value(result_json, "outputs")
    goal = _dict_value(normalized_input_json, "goal")

    return DashboardItem(
        status="ready",
        missing_inputs=[],
        snapshot_id=snapshot.id,
        calculated_at=snapshot.calculated_at,
        formula_version=snapshot.formula_version,
        goal=DashboardGoalSummary(
            id=str(goal["id"]),
            name=str(goal["name"]),
            target_cents=int(goal["target_cents"]),
            current_saved_cents=int(goal["current_saved_cents"]),
            target_date=date.fromisoformat(str(goal["target_date"])),
        ),
        pace=DashboardPaceSummary(
            pace_status=str(outputs["pace_status"]),
            weekly_safe_to_spend_cents=int(outputs["weekly_safe_to_spend_cents"]),
            projected_shortfall_cents=int(outputs["projected_shortfall_cents"]),
            remaining_weeks=int(outputs["remaining_weeks"]),
            progress_percentage=float(outputs["progress_percentage"]),
            current_week_opening_allowance_cents=int(
                outputs["current_week_opening_allowance_cents"],
            ),
            current_week_remainder_cents=int(outputs["current_week_remainder_cents"]),
        ),
        explanation=_dict_value(result_json, "explanation"),
        changed_from_previous=_dict_value(result_json, "changed_from_previous"),
    )


def _dict_value(source: dict[str, Any], key: str) -> dict[str, Any]:
    value = source[key]
    if not isinstance(value, dict):
        raise TypeError(f"Expected {key} to be a JSON object.")
    return value
