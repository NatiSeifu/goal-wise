"""Goal input service behavior."""

from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models import Goal
from app.repositories.goals import (
    archive_goal,
    create_goal,
    get_active_goal,
    get_goal_for_user,
    update_goal,
)
from app.services.local_dates import user_local_date


class GoalInputError(Exception):
    """Base class for expected goal input service failures."""


class GoalInputValidationError(GoalInputError):
    def __init__(self, fields: dict[str, list[str]]) -> None:
        self.fields = fields
        super().__init__("Goal input validation failed.")


class GoalNotFoundError(GoalInputError):
    """Raised when a goal does not exist for the authenticated user."""


def get_active_goal_for_user(db_session: Session, *, user_id: str) -> Goal | None:
    return get_active_goal(db_session, user_id=user_id)


def create_goal_for_user(
    db_session: Session,
    *,
    user_id: str,
    name: str,
    target_cents: int,
    initial_saved_cents: int,
    current_saved_cents: int,
    start_date: date,
    target_date: date,
    user_time_zone: str,
    now: datetime,
) -> Goal:
    fields = _validate_goal_fields(
        name=name,
        target_cents=target_cents,
        initial_saved_cents=initial_saved_cents,
        current_saved_cents=current_saved_cents,
        start_date=start_date,
        target_date=target_date,
        user_time_zone=user_time_zone,
        now=now,
    )
    if get_active_goal(db_session, user_id=user_id) is not None:
        fields.setdefault("goal", []).append("An active goal already exists.")
    if fields:
        raise GoalInputValidationError(fields)

    return create_goal(
        db_session,
        user_id=user_id,
        name=name.strip(),
        target_cents=target_cents,
        initial_saved_cents=initial_saved_cents,
        current_saved_cents=current_saved_cents,
        start_date=start_date,
        target_date=target_date,
        status=_status_for_amounts(
            target_cents=target_cents,
            current_saved_cents=current_saved_cents,
        ),
    )


def update_goal_for_user(
    db_session: Session,
    *,
    user_id: str,
    goal_id: str,
    name: str,
    target_cents: int,
    initial_saved_cents: int,
    current_saved_cents: int,
    start_date: date,
    target_date: date,
    user_time_zone: str,
    now: datetime,
) -> Goal:
    goal = get_goal_for_user(db_session, user_id=user_id, goal_id=goal_id)
    if goal is None:
        raise GoalNotFoundError

    fields = _validate_goal_fields(
        name=name,
        target_cents=target_cents,
        initial_saved_cents=initial_saved_cents,
        current_saved_cents=current_saved_cents,
        start_date=start_date,
        target_date=target_date,
        user_time_zone=user_time_zone,
        now=now,
    )
    if fields:
        raise GoalInputValidationError(fields)

    return update_goal(
        db_session,
        goal=goal,
        name=name.strip(),
        target_cents=target_cents,
        initial_saved_cents=initial_saved_cents,
        current_saved_cents=current_saved_cents,
        start_date=start_date,
        target_date=target_date,
        status=_status_for_amounts(
            target_cents=target_cents,
            current_saved_cents=current_saved_cents,
        ),
    )


def archive_goal_for_user(
    db_session: Session,
    *,
    user_id: str,
    goal_id: str,
    now: datetime,
) -> Goal:
    goal = get_goal_for_user(db_session, user_id=user_id, goal_id=goal_id)
    if goal is None:
        raise GoalNotFoundError

    return archive_goal(db_session, goal=goal, archived_at=now)


def _validate_goal_fields(
    *,
    name: str,
    target_cents: int,
    initial_saved_cents: int,
    current_saved_cents: int,
    start_date: date,
    target_date: date,
    user_time_zone: str,
    now: datetime,
) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}

    if not name.strip():
        fields.setdefault("name", []).append("Must not be blank.")
    if len(name.strip()) > 120:
        fields.setdefault("name", []).append("Must be 120 characters or fewer.")
    if target_cents <= 0:
        fields.setdefault("target_cents", []).append("Must be greater than zero.")
    if initial_saved_cents < 0:
        fields.setdefault("initial_saved_cents", []).append(
            "Must be greater than or equal to zero.",
        )
    if current_saved_cents < 0:
        fields.setdefault("current_saved_cents", []).append(
            "Must be greater than or equal to zero.",
        )
    elif current_saved_cents > target_cents:
        fields.setdefault("current_saved_cents", []).append("Cannot be greater than target_cents.")
    if initial_saved_cents > target_cents and target_cents > 0:
        fields.setdefault("initial_saved_cents", []).append("Cannot be greater than target_cents.")
    if target_date <= user_local_date(now=now, user_time_zone=user_time_zone):
        fields.setdefault("target_date", []).append("Must be after the user's current local date.")
    if start_date >= target_date:
        fields.setdefault("start_date", []).append("Must be before target_date.")

    return fields


def _status_for_amounts(*, target_cents: int, current_saved_cents: int) -> str:
    if current_saved_cents >= target_cents:
        return "completed"
    return "active"
