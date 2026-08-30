"""Weekly plan service behavior."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import CalculationSnapshot, WeeklyPlan
from app.repositories.weekly_plans import create_weekly_plan, get_weekly_plan
from app.schemas.snapshots import parse_snapshot_result
from app.services.local_dates import local_week_start


def get_or_create_current_week_plan(
    db_session: Session,
    *,
    user_id: str,
    user_time_zone: str,
    snapshot: CalculationSnapshot,
    now: datetime,
) -> WeeklyPlan:
    week_start = local_week_start(now=now, user_time_zone=user_time_zone)
    existing_plan = get_weekly_plan(
        db_session,
        user_id=user_id,
        goal_id=snapshot.goal_id,
        week_start=week_start,
    )
    if existing_plan is not None:
        return existing_plan

    return create_weekly_plan(
        db_session,
        user_id=user_id,
        goal_id=snapshot.goal_id,
        week_start=week_start,
        opening_allowance_cents=_weekly_safe_to_spend_cents(snapshot),
        created_from_snapshot_id=snapshot.id,
    )


def _weekly_safe_to_spend_cents(snapshot: CalculationSnapshot) -> int:
    return parse_snapshot_result(snapshot.result_json).outputs.weekly_safe_to_spend_cents
