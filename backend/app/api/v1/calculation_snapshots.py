"""Calculation snapshot API routes."""

from fastapi import APIRouter

from app.api.dependencies import CurrentSessionDep, DbSessionDep
from app.models import CalculationSnapshot
from app.repositories.calculation_snapshots import get_latest_snapshot_for_user
from app.schemas.calculation_snapshots import (
    CalculationSnapshotItemResponse,
    CalculationSnapshotResponse,
)

router = APIRouter(prefix="/calculation-snapshots", tags=["calculation-snapshots"])


@router.get("/latest", response_model=CalculationSnapshotItemResponse)
def get_latest_calculation_snapshot(
    current_session: CurrentSessionDep,
    db_session: DbSessionDep,
) -> CalculationSnapshotItemResponse:
    snapshot = get_latest_snapshot_for_user(
        db_session,
        user_id=current_session.user.id,
    )
    return CalculationSnapshotItemResponse(item=_snapshot_response(snapshot))


def _snapshot_response(
    snapshot: CalculationSnapshot | None,
) -> CalculationSnapshotResponse | None:
    if snapshot is None:
        return None
    return CalculationSnapshotResponse.model_validate(snapshot)
