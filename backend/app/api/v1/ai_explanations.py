"""AI explanation API routes."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.dependencies import (
    AiProviderDep,
    CsrfSessionDep,
    CurrentSessionDep,
    DbSessionDep,
    NowDep,
    SettingsDep,
    ai_explanations_are_available,
)
from app.api.errors import error_response
from app.schemas.ai_explanations import (
    AIExplanationAvailabilityResponse,
    AIExplanationItem,
    AIExplanationItemResponse,
)
from app.services.ai_explanations import (
    NoSnapshotForExplanation,
    generate_or_reuse_latest_explanation,
)

router = APIRouter(prefix="/ai-explanations", tags=["ai-explanations"])


@router.get("/status", response_model=AIExplanationAvailabilityResponse)
def get_explanation_status(
    _current_session: CurrentSessionDep,
    settings: SettingsDep,
) -> AIExplanationAvailabilityResponse:
    return AIExplanationAvailabilityResponse(
        enabled=ai_explanations_are_available(settings),
    )


@router.post("/latest", response_model=AIExplanationItemResponse)
def request_latest_explanation(
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
    now: NowDep,
    settings: SettingsDep,
    provider: AiProviderDep,
) -> AIExplanationItemResponse | JSONResponse:
    try:
        result = generate_or_reuse_latest_explanation(
            db_session,
            user_id=current_session.user.id,
            provider=provider,
            settings=settings,
            generated_at=now,
        )
    except NoSnapshotForExplanation:
        return error_response(
            status_code=404,
            code="calculation_snapshot_not_found",
            message="No calculation snapshot is available to explain.",
        )

    if result.explanation is not None:
        db_session.commit()

    return AIExplanationItemResponse(
        enabled=ai_explanations_are_available(settings),
        item=AIExplanationItem(
            snapshot_id=result.snapshot.id,
            calculated_at=result.snapshot.calculated_at,
            formula_version=result.snapshot.formula_version,
            source=result.source.value,
            explanation=result.response,
        ),
    )
