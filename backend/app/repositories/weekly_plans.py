"""Weekly plan persistence queries."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import WeeklyPlan


def create_weekly_plan(
    db_session: Session,
    *,
    user_id: str,
    goal_id: str,
    week_start: date,
    opening_allowance_cents: int,
    created_from_snapshot_id: str,
) -> WeeklyPlan:
    weekly_plan = WeeklyPlan(
        user_id=user_id,
        goal_id=goal_id,
        week_start=week_start,
        opening_allowance_cents=opening_allowance_cents,
        created_from_snapshot_id=created_from_snapshot_id,
    )
    db_session.add(weekly_plan)
    db_session.flush()
    return weekly_plan


def get_weekly_plan(
    db_session: Session,
    *,
    user_id: str,
    goal_id: str,
    week_start: date,
) -> WeeklyPlan | None:
    return db_session.scalar(
        select(WeeklyPlan).where(
            WeeklyPlan.user_id == user_id,
            WeeklyPlan.goal_id == goal_id,
            WeeklyPlan.week_start == week_start,
        ),
    )
