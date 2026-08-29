"""Generate and reuse snapshot-scoped AI explanations."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Literal

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import AIExplanation, CalculationSnapshot
from app.repositories.ai_explanations import (
    create_ai_explanation,
    get_ai_explanation_for_version,
)
from app.repositories.calculation_snapshots import get_latest_snapshot_for_user
from app.services.ai_explanation_contract import (
    AI_EXPLANATION_SCHEMA_VERSION,
    AiContractError,
    AiExplanationResponse,
    build_ai_payload,
    validate_ai_response,
)
from app.services.ai_provider import AiProvider, AiProviderError


class AiExplanationSource(StrEnum):
    GENERATED = "generated"
    FALLBACK = "fallback"


class NoSnapshotForExplanation(LookupError):
    """Raised when a user has no committed calculation snapshot to explain."""


@dataclass(frozen=True, slots=True)
class AiExplanationResult:
    """The explanation and the trusted snapshot it describes."""

    snapshot: CalculationSnapshot
    response: AiExplanationResponse
    source: AiExplanationSource
    explanation: AIExplanation | None


def generate_or_reuse_latest_explanation(
    db_session: Session,
    *,
    user_id: str,
    provider: AiProvider | None,
    settings: Settings,
    generated_at: datetime | None = None,
) -> AiExplanationResult:
    """Explain the user's latest snapshot without recalculating it."""

    snapshot = get_latest_snapshot_for_user(db_session, user_id=user_id)
    if snapshot is None:
        raise NoSnapshotForExplanation

    provider_name = settings.ai_summary_provider
    model_name = settings.ai_summary_model
    prompt_version = settings.ai_summary_prompt_version
    response_schema_version = settings.ai_summary_response_schema_version

    stored = get_ai_explanation_for_version(
        db_session,
        user_id=user_id,
        snapshot_id=snapshot.id,
        provider=provider_name,
        model=model_name,
        prompt_version=prompt_version,
        response_schema_version=response_schema_version,
    )
    if stored is not None:
        try:
            response = validate_ai_response(stored.response_json)
        except AiContractError:
            return _fallback_result(snapshot)
        return AiExplanationResult(
            snapshot=snapshot,
            response=response,
            source=AiExplanationSource.GENERATED,
            explanation=stored,
        )

    if not settings.ai_summary_enabled:
        return _fallback_result(snapshot)

    try:
        payload = build_ai_payload(snapshot.result_json)
        if provider is None:
            return _fallback_result(snapshot)
        raw_response = provider.generate(
            payload=payload,
            timeout_seconds=settings.ai_summary_timeout_seconds,
        )
        response = validate_ai_response(raw_response)
    except (AiProviderError, AiContractError):
        return _fallback_result(snapshot)

    explanation = create_ai_explanation(
        db_session,
        user_id=user_id,
        snapshot_id=snapshot.id,
        provider=provider_name,
        model=model_name,
        prompt_version=prompt_version,
        response_schema_version=response_schema_version,
        response_json=response.model_dump(),
        generated_at=generated_at or snapshot.created_at,
    )
    return AiExplanationResult(
        snapshot=snapshot,
        response=response,
        source=AiExplanationSource.GENERATED,
        explanation=explanation,
    )


def _fallback_result(snapshot: CalculationSnapshot) -> AiExplanationResult:
    return AiExplanationResult(
        snapshot=snapshot,
        response=_deterministic_fallback(snapshot),
        source=AiExplanationSource.FALLBACK,
        explanation=None,
    )


def _deterministic_fallback(snapshot: CalculationSnapshot) -> AiExplanationResponse:
    pace_status = _pace_status(snapshot)
    headline_by_status = {
        "Completed": "Your goal is complete",
        "Ahead": "Your plan is ahead",
        "On Track": "Your plan is on track",
        "At Risk": "Your plan needs attention",
        "Off Pace": "Your plan needs a closer look",
    }
    tone: Literal["positive", "neutral", "caution"] = (
        "positive" if pace_status in {"Completed", "Ahead", "On Track"} else "caution"
    )
    return validate_ai_response(
        {
            "schema_version": AI_EXPLANATION_SCHEMA_VERSION,
            "headline": headline_by_status.get(pace_status, "Your plan is ready to review"),
            "body": "Review your current plan and keep the saved assumptions up to date.",
            "observations": [
                {
                    "kind": "pace",
                    "tone": tone,
                    "metric_refs": ["pace_status"],
                }
            ],
            "next_step": "Review your plan when your goal or expected cash flow changes.",
        }
    )


def _pace_status(snapshot: CalculationSnapshot) -> str:
    outputs = snapshot.result_json.get("outputs")
    if isinstance(outputs, dict):
        pace_status: object = outputs.get("pace_status")
        if isinstance(pace_status, str):
            return pace_status
    return ""
