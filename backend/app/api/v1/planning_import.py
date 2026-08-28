"""Planning CSV preview route."""

from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse

from app.api.dependencies import CsrfSessionDep, DbSessionDep, NowDep, SettingsDep
from app.api.errors import planning_import_error_response
from app.repositories.calculation_snapshots import get_latest_snapshot_for_user_and_goal
from app.schemas.planning_import import (
    PlanningImportCashPreview,
    PlanningImportConfirmRequest,
    PlanningImportConfirmResponse,
    PlanningImportGoalPreview,
    PlanningImportPreviewResponse,
    PlanningImportSourcePreview,
)
from app.services.local_dates import user_local_date
from app.services.planning_import_parser import (
    MAX_PLANNING_IMPORT_BYTES,
    PlanningCsvParseError,
    parse_planning_csv,
)
from app.services.planning_import_persistence import (
    PlanningImportPersistenceError,
    replace_planning_setup_for_user,
)
from app.services.planning_import_tokens import (
    InvalidPlanningImportToken,
    create_planning_import_token,
    read_planning_import_token,
)
from app.services.planning_import_validation import (
    PlanningCsvValidationError,
    validate_planning_csv,
    validation_issue_dict,
)

router = APIRouter(prefix="/planning-import", tags=["planning-import"])


@router.post("/preview", response_model=PlanningImportPreviewResponse)
async def preview_planning_import(
    file: UploadFile,
    current_session: CsrfSessionDep,
    now: NowDep,
    settings: SettingsDep,
) -> PlanningImportPreviewResponse | JSONResponse:
    data = await file.read(MAX_PLANNING_IMPORT_BYTES + 1)
    try:
        parsed = parse_planning_csv(data)
        planning_import = validate_planning_csv(
            parsed,
            user_local_date=user_local_date(
                now=now,
                user_time_zone=current_session.user.time_zone,
            ),
        )
    except PlanningCsvParseError as exc:
        issue = {
            "row": exc.row_number or 1,
            "field": "document",
            "code": exc.code,
            "message": exc.message,
        }
        return planning_import_error_response(issues=[issue])
    except PlanningCsvValidationError as exc:
        return planning_import_error_response(
            issues=[validation_issue_dict(issue) for issue in exc.issues]
        )

    return PlanningImportPreviewResponse(
        preview_token=create_planning_import_token(
            planning_import,
            user_id=current_session.user.id,
            session_secret=settings.session_secret,
            issued_at=now,
        ),
        valid=True,
        row_count=len(parsed.rows),
        counts={
            "goal": 1,
            "cash": 1,
            "income": len(planning_import.income_sources),
            "expense": len(planning_import.planned_expenses),
        },
        goal=PlanningImportGoalPreview(
            name=planning_import.goal.name,
            target_cents=planning_import.goal.target_cents,
            initial_saved_cents=planning_import.goal.initial_saved_cents,
            current_saved_cents=planning_import.goal.current_saved_cents,
            start_date=planning_import.goal.start_date,
            target_date=planning_import.goal.target_date,
        ),
        cash=PlanningImportCashPreview(
            starting_cash_cents=planning_import.cash.starting_cash_cents,
            balance_as_of_date=planning_import.cash.balance_as_of_date,
            reserve_buffer_cents=planning_import.cash.reserve_buffer_cents,
        ),
        income_sources=[
            PlanningImportSourcePreview(
                name=source.name,
                amount_cents=source.amount_cents,
                next_date=source.next_date,
                frequency=source.frequency.value,
                confidence=source.confidence.value,
            )
            for source in planning_import.income_sources
        ],
        planned_expenses=[
            PlanningImportSourcePreview(
                name=expense.name,
                amount_cents=expense.amount_cents,
                next_date=expense.next_date,
                frequency=expense.frequency.value,
                classification=expense.classification.value,
            )
            for expense in planning_import.planned_expenses
        ],
        errors=[],
    )


@router.post("/confirm", response_model=PlanningImportConfirmResponse)
def confirm_planning_import(
    payload: PlanningImportConfirmRequest,
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
    now: NowDep,
    settings: SettingsDep,
) -> PlanningImportConfirmResponse | JSONResponse:
    try:
        planning_import = read_planning_import_token(
            payload.preview_token,
            user_id=current_session.user.id,
            session_secret=settings.session_secret,
            now=now,
        )
        goal = replace_planning_setup_for_user(
            db_session,
            planning_import,
            user_id=current_session.user.id,
            user_time_zone=current_session.user.time_zone,
            now=now,
        )
    except InvalidPlanningImportToken:
        db_session.rollback()
        return planning_import_error_response(
            issues=[
                {
                    "row": 1,
                    "field": "preview_token",
                    "code": "invalid_preview",
                    "message": "The preview is invalid or has expired. Upload the CSV again.",
                }
            ]
        )
    except PlanningImportPersistenceError:
        db_session.rollback()
        return planning_import_error_response(
            issues=[
                {
                    "row": 1,
                    "field": "document",
                    "code": "import_not_committed",
                    "message": "The import could not be committed. Your previous plan was kept.",
                }
            ]
        )
    except Exception:
        db_session.rollback()
        raise

    latest_snapshot = get_latest_snapshot_for_user_and_goal(
        db_session,
        user_id=current_session.user.id,
        goal_id=goal.id,
    )
    if latest_snapshot is None:
        db_session.rollback()
        return planning_import_error_response(
            issues=[
                {
                    "row": 1,
                    "field": "document",
                    "code": "import_not_committed",
                    "message": "The import could not be committed. Your previous plan was kept.",
                }
            ]
        )
    db_session.commit()
    return PlanningImportConfirmResponse(goal_id=goal.id, snapshot_id=latest_snapshot.id)
