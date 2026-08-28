"""Persistence workflow for confirmed planning imports."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Goal
from app.repositories.calculation_snapshots import get_latest_snapshot_for_user_and_goal
from app.repositories.financial_inputs import (
    deactivate_income_source,
    deactivate_planned_expense,
    list_active_income_sources,
    list_active_planned_expenses,
)
from app.repositories.goals import get_active_goal
from app.services.financial_inputs import (
    create_income_source_for_user,
    create_planned_expense_for_user,
    upsert_financial_profile_for_user,
)
from app.services.goal_inputs import create_goal_for_user, update_goal_for_user
from app.services.planning_import import PlanningImport
from app.services.snapshot_calculation import (
    SnapshotCalculationStatus,
    calculate_and_snapshot_for_user,
)


class PlanningImportPersistenceError(RuntimeError):
    """Raised when a confirmed import cannot produce a committed plan."""


def replace_planning_setup_for_user(
    db_session: Session,
    planning_import: PlanningImport,
    *,
    user_id: str,
    user_time_zone: str,
    now: datetime,
) -> Goal:
    active_goal = get_active_goal(db_session, user_id=user_id)
    if active_goal is None:
        goal = create_goal_for_user(
            db_session,
            user_id=user_id,
            name=planning_import.goal.name,
            target_cents=planning_import.goal.target_cents,
            initial_saved_cents=planning_import.goal.initial_saved_cents,
            current_saved_cents=planning_import.goal.current_saved_cents,
            start_date=planning_import.goal.start_date,
            target_date=planning_import.goal.target_date,
            user_time_zone=user_time_zone,
            now=now,
        )
    else:
        goal = update_goal_for_user(
            db_session,
            user_id=user_id,
            goal_id=active_goal.id,
            name=planning_import.goal.name,
            target_cents=planning_import.goal.target_cents,
            initial_saved_cents=planning_import.goal.initial_saved_cents,
            current_saved_cents=planning_import.goal.current_saved_cents,
            start_date=planning_import.goal.start_date,
            target_date=planning_import.goal.target_date,
            user_time_zone=user_time_zone,
            now=now,
        )

    upsert_financial_profile_for_user(
        db_session,
        user_id=user_id,
        starting_cash_cents=planning_import.cash.starting_cash_cents,
        balance_as_of_date=planning_import.cash.balance_as_of_date,
        reserve_buffer_cents=planning_import.cash.reserve_buffer_cents,
        reserve_buffer_confirmed=True,
        user_time_zone=user_time_zone,
        now=now,
    )
    for existing_source in list_active_income_sources(db_session, user_id=user_id):
        deactivate_income_source(db_session, income_source=existing_source)
    for existing_expense in list_active_planned_expenses(db_session, user_id=user_id):
        deactivate_planned_expense(db_session, planned_expense=existing_expense)
    for source in planning_import.income_sources:
        create_income_source_for_user(
            db_session,
            user_id=user_id,
            name=source.name,
            amount_cents=source.amount_cents,
            next_date=source.next_date,
            frequency=source.frequency.value,
            confidence=source.confidence.value,
        )
    for expense in planning_import.planned_expenses:
        create_planned_expense_for_user(
            db_session,
            user_id=user_id,
            name=expense.name,
            amount_cents=expense.amount_cents,
            next_date=expense.next_date,
            frequency=expense.frequency.value,
            classification=expense.classification.value,
        )

    result = calculate_and_snapshot_for_user(
        db_session,
        user_id=user_id,
        user_time_zone=user_time_zone,
        trigger="planning_import_confirmed",
        calculated_at=now,
    )
    if result.status is not SnapshotCalculationStatus.CREATED:
        raise PlanningImportPersistenceError(
            "Planning import did not produce a calculation snapshot."
        )
    if get_latest_snapshot_for_user_and_goal(db_session, user_id=user_id, goal_id=goal.id) is None:
        raise PlanningImportPersistenceError("Confirmed import has no latest snapshot.")
    return goal
