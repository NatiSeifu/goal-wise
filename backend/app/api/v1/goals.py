"""Goal input API routes."""

from datetime import datetime

from fastapi import APIRouter, Response

from app.api.dependencies import CsrfSessionDep, CurrentSessionDep, DbSessionDep, NowDep
from app.api.errors import error_response, validation_error_response
from app.models import Goal
from app.schemas.goal_inputs import GoalItemResponse, GoalRequest, GoalResponse
from app.services.goal_inputs import (
    GoalInputValidationError,
    GoalNotFoundError,
    create_goal_for_user,
    get_active_goal_for_user,
    update_goal_for_user,
)
from app.services.snapshot_calculation import calculate_and_snapshot_for_user

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("/active", response_model=GoalItemResponse)
def get_active_goal(
    current_session: CurrentSessionDep,
    db_session: DbSessionDep,
) -> GoalItemResponse:
    goal = get_active_goal_for_user(
        db_session,
        user_id=current_session.user.id,
    )
    return GoalItemResponse(item=_goal_response(goal))


@router.post("", response_model=GoalItemResponse, status_code=201)
def create_goal(
    payload: GoalRequest,
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
    now: NowDep,
) -> GoalItemResponse | Response:
    try:
        goal = create_goal_for_user(
            db_session,
            user_id=current_session.user.id,
            name=payload.name,
            target_cents=payload.target_cents,
            initial_saved_cents=payload.initial_saved_cents,
            current_saved_cents=payload.current_saved_cents,
            start_date=payload.start_date,
            target_date=payload.target_date,
            user_time_zone=current_session.user.time_zone,
            now=now,
        )
        _snapshot_after_write(
            db_session,
            user_id=current_session.user.id,
            user_time_zone=current_session.user.time_zone,
            trigger="goal_created",
            calculated_at=now,
        )
    except GoalInputValidationError as exc:
        db_session.rollback()
        return validation_error_response(fields=exc.fields)

    db_session.commit()
    return GoalItemResponse(item=_goal_response(goal))


@router.patch("/{goal_id}", response_model=GoalItemResponse)
def update_goal(
    goal_id: str,
    payload: GoalRequest,
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
    now: NowDep,
) -> GoalItemResponse | Response:
    try:
        goal = update_goal_for_user(
            db_session,
            user_id=current_session.user.id,
            goal_id=goal_id,
            name=payload.name,
            target_cents=payload.target_cents,
            initial_saved_cents=payload.initial_saved_cents,
            current_saved_cents=payload.current_saved_cents,
            start_date=payload.start_date,
            target_date=payload.target_date,
            user_time_zone=current_session.user.time_zone,
            now=now,
        )
        _snapshot_after_write(
            db_session,
            user_id=current_session.user.id,
            user_time_zone=current_session.user.time_zone,
            trigger="goal_updated",
            calculated_at=now,
        )
    except GoalNotFoundError:
        db_session.rollback()
        return error_response(
            status_code=404,
            code="not_found",
            message="Goal not found.",
        )
    except GoalInputValidationError as exc:
        db_session.rollback()
        return validation_error_response(fields=exc.fields)

    db_session.commit()
    return GoalItemResponse(item=_goal_response(goal))


def _goal_response(goal: Goal | None) -> GoalResponse | None:
    if goal is None:
        return None
    return GoalResponse.model_validate(goal)


def _snapshot_after_write(
    db_session: DbSessionDep,
    *,
    user_id: str,
    user_time_zone: str,
    trigger: str,
    calculated_at: datetime,
) -> None:
    calculate_and_snapshot_for_user(
        db_session,
        user_id=user_id,
        user_time_zone=user_time_zone,
        trigger=trigger,
        calculated_at=calculated_at,
    )
