"""Goal persistence queries."""

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Goal


def create_goal(
    db_session: Session,
    *,
    user_id: str,
    name: str,
    target_cents: int,
    initial_saved_cents: int,
    current_saved_cents: int,
    start_date: date,
    target_date: date,
    status: str,
) -> Goal:
    goal = Goal(
        user_id=user_id,
        name=name,
        target_cents=target_cents,
        initial_saved_cents=initial_saved_cents,
        current_saved_cents=current_saved_cents,
        start_date=start_date,
        target_date=target_date,
        status=status,
    )
    db_session.add(goal)
    db_session.flush()
    return goal


def get_active_goal(db_session: Session, *, user_id: str) -> Goal | None:
    return db_session.scalar(
        select(Goal).where(
            Goal.user_id == user_id,
            Goal.status == "active",
        ),
    )


def get_goal_for_user(
    db_session: Session,
    *,
    user_id: str,
    goal_id: str,
) -> Goal | None:
    return db_session.scalar(
        select(Goal).where(
            Goal.id == goal_id,
            Goal.user_id == user_id,
        ),
    )


def update_goal(
    db_session: Session,
    *,
    goal: Goal,
    name: str,
    target_cents: int,
    initial_saved_cents: int,
    current_saved_cents: int,
    start_date: date,
    target_date: date,
    status: str,
    archived_at: datetime | None = None,
) -> Goal:
    goal.name = name
    goal.target_cents = target_cents
    goal.initial_saved_cents = initial_saved_cents
    goal.current_saved_cents = current_saved_cents
    goal.start_date = start_date
    goal.target_date = target_date
    goal.status = status
    goal.archived_at = archived_at
    db_session.flush()
    return goal
