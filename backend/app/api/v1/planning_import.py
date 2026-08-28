"""Planning CSV preview route."""

from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse

from app.api.dependencies import CsrfSessionDep, NowDep
from app.api.errors import planning_import_error_response
from app.schemas.planning_import import (
    PlanningImportCashPreview,
    PlanningImportGoalPreview,
    PlanningImportPreviewResponse,
    PlanningImportSourcePreview,
)
from app.services.local_dates import user_local_date
from app.services.planning_import_parser import PlanningCsvParseError, parse_planning_csv
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
) -> PlanningImportPreviewResponse | JSONResponse:
    data = await file.read(1_048_577)
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
