"""Calculation snapshot persistence queries."""

from datetime import datetime
from typing import Any

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.models import CalculationSnapshot


def create_calculation_snapshot(
    db_session: Session,
    *,
    user_id: str,
    goal_id: str,
    formula_version: str,
    trigger: str,
    normalized_input_json: dict[str, Any],
    result_json: dict[str, Any],
    calculated_at: datetime,
) -> CalculationSnapshot:
    snapshot = CalculationSnapshot(
        user_id=user_id,
        goal_id=goal_id,
        formula_version=formula_version,
        trigger=trigger,
        normalized_input_json=normalized_input_json,
        result_json=result_json,
        calculated_at=calculated_at,
    )
    db_session.add(snapshot)
    db_session.flush()
    return snapshot


def get_latest_snapshot_for_user(
    db_session: Session,
    *,
    user_id: str,
) -> CalculationSnapshot | None:
    return db_session.scalar(
        _latest_snapshot_query().where(CalculationSnapshot.user_id == user_id),
    )


def get_latest_snapshot_for_user_and_goal(
    db_session: Session,
    *,
    user_id: str,
    goal_id: str,
) -> CalculationSnapshot | None:
    return db_session.scalar(
        _latest_snapshot_query().where(
            CalculationSnapshot.user_id == user_id,
            CalculationSnapshot.goal_id == goal_id,
        ),
    )


def get_previous_snapshot_for_user(
    db_session: Session,
    *,
    user_id: str,
    snapshot: CalculationSnapshot,
) -> CalculationSnapshot | None:
    if snapshot.user_id != user_id:
        return None

    return db_session.scalar(
        select(CalculationSnapshot)
        .where(
            CalculationSnapshot.user_id == user_id,
            CalculationSnapshot.id != snapshot.id,
            or_(
                CalculationSnapshot.calculated_at < snapshot.calculated_at,
                (
                    (CalculationSnapshot.calculated_at == snapshot.calculated_at)
                    & (CalculationSnapshot.id < snapshot.id)
                ),
            ),
        )
        .order_by(
            CalculationSnapshot.calculated_at.desc(),
            CalculationSnapshot.id.desc(),
        )
        .limit(1),
    )


def list_snapshots_for_user(
    db_session: Session,
    *,
    user_id: str,
    limit: int,
) -> list[CalculationSnapshot]:
    return list(
        db_session.scalars(
            _latest_snapshot_query()
            .where(CalculationSnapshot.user_id == user_id)
            .limit(limit),
        ),
    )


def _latest_snapshot_query() -> Select[tuple[CalculationSnapshot]]:
    return select(CalculationSnapshot).order_by(
        CalculationSnapshot.calculated_at.desc(),
        CalculationSnapshot.id.desc(),
    )
