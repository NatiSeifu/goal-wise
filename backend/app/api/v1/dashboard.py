"""Dashboard API routes."""

from datetime import datetime

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
from app.schemas.snapshots import parse_snapshot_input, parse_snapshot_result
from app.services.auth import CurrentSession
from app.services.recalculation_boundary import (
    RecalculationStatus,
    prepare_pace_input_for_user,
)
from app.services.weekly_plans import get_or_create_current_week_plan

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

    weekly_plan = get_or_create_current_week_plan(
        db_session,
        user_id=current_session.user.id,
        user_time_zone=current_session.user.time_zone,
        snapshot=snapshot,
        now=now,
    )
    db_session.commit()
    return DashboardResponse(
        item=_ready_dashboard_item(
            snapshot,
            current_week_opening_allowance_cents=weekly_plan.opening_allowance_cents,
            current_week_remainder_cents=weekly_plan.opening_allowance_cents,
        ),
    )


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


def _ready_dashboard_item(
    snapshot: CalculationSnapshot,
    *,
    current_week_opening_allowance_cents: int,
    current_week_remainder_cents: int,
) -> DashboardItem:
    result = parse_snapshot_result(snapshot.result_json)
    snapshot_input = parse_snapshot_input(snapshot.normalized_input_json)
    outputs = result.outputs
    goal = snapshot_input.goal

    return DashboardItem(
        status="ready",
        missing_inputs=[],
        snapshot_id=snapshot.id,
        calculated_at=snapshot.calculated_at,
        formula_version=snapshot.formula_version,
        goal=DashboardGoalSummary(
            id=goal.id,
            name=goal.name,
            target_cents=goal.target_cents,
            current_saved_cents=goal.current_saved_cents,
            target_date=goal.target_date,
        ),
        pace=DashboardPaceSummary(
            pace_status=outputs.pace_status,
            weekly_safe_to_spend_cents=outputs.weekly_safe_to_spend_cents,
            expected_savings_to_date_cents=outputs.expected_savings_to_date_cents,
            projected_shortfall_cents=outputs.projected_shortfall_cents,
            remaining_weeks=outputs.remaining_weeks,
            progress_percentage=outputs.progress_percentage,
            current_week_opening_allowance_cents=current_week_opening_allowance_cents,
            current_week_remainder_cents=current_week_remainder_cents,
        ),
        explanation=result.explanation.model_dump(mode="json"),
        changed_from_previous=result.changed_from_previous.model_dump(mode="json"),
    )
