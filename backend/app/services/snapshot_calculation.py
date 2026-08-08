"""Run deterministic pace calculation and persist immutable snapshots."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from sqlalchemy.orm import Session

from app.models import CalculationSnapshot
from app.pace_engine.calculator import calculate_pace
from app.repositories.calculation_snapshots import (
    create_calculation_snapshot,
    get_latest_snapshot_for_user_and_goal,
)
from app.services.recalculation_boundary import (
    MissingInput,
    RecalculationStatus,
    prepare_pace_input_for_user,
)
from app.services.snapshot_json import build_snapshot_json


class SnapshotCalculationStatus(StrEnum):
    CREATED = "created"
    MISSING_INPUTS = "missing_inputs"


@dataclass(frozen=True, slots=True)
class SnapshotCalculationResult:
    status: SnapshotCalculationStatus
    missing_inputs: tuple[MissingInput, ...]
    snapshot: CalculationSnapshot | None


def calculate_and_snapshot_for_user(
    db_session: Session,
    *,
    user_id: str,
    user_time_zone: str,
    trigger: str,
    calculated_at: datetime,
) -> SnapshotCalculationResult:
    readiness = prepare_pace_input_for_user(
        db_session,
        user_id=user_id,
        user_time_zone=user_time_zone,
        calculated_at=calculated_at,
    )
    if readiness.status is RecalculationStatus.MISSING_INPUTS:
        return SnapshotCalculationResult(
            status=SnapshotCalculationStatus.MISSING_INPUTS,
            missing_inputs=readiness.missing_inputs,
            snapshot=None,
        )

    if (
        readiness.pace_input is None
        or readiness.goal is None
        or readiness.financial_profile is None
    ):
        raise RuntimeError("ready recalculation state is missing required records")

    pace_result = calculate_pace(readiness.pace_input)
    previous_snapshot = get_latest_snapshot_for_user_and_goal(
        db_session,
        user_id=user_id,
        goal_id=readiness.goal.id,
    )
    snapshot_json = build_snapshot_json(
        trigger=trigger,
        calculated_at=calculated_at,
        user_time_zone=user_time_zone,
        goal=readiness.goal,
        financial_profile=readiness.financial_profile,
        income_sources=readiness.income_sources,
        planned_expenses=readiness.planned_expenses,
        pace_result=pace_result,
        previous_snapshot=previous_snapshot,
    )
    snapshot = create_calculation_snapshot(
        db_session,
        user_id=user_id,
        goal_id=readiness.goal.id,
        formula_version=pace_result.formula_version,
        trigger=trigger,
        normalized_input_json=snapshot_json.normalized_input_json,
        result_json=snapshot_json.result_json,
        calculated_at=calculated_at,
    )

    return SnapshotCalculationResult(
        status=SnapshotCalculationStatus.CREATED,
        missing_inputs=(),
        snapshot=snapshot,
    )
