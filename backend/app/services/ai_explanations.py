"""Generate and reuse snapshot-scoped AI explanations."""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import AIExplanation, CalculationSnapshot
from app.repositories.ai_explanations import (
    create_ai_explanation,
    get_ai_explanation_for_version,
)
from app.repositories.calculation_snapshots import get_latest_snapshot_for_user
from app.schemas.snapshots import SnapshotContractError, parse_snapshot_result
from app.services.ai_explanation_contract import (
    AiContractError,
    AiExplanationResponse,
    build_ai_payload,
    validate_ai_response,
)
from app.services.ai_provider import AiProvider, AiProviderError

logger = logging.getLogger(__name__)


class AiExplanationSource(StrEnum):
    GENERATED = "generated"


class NoSnapshotForExplanation(LookupError):
    """Raised when a user has no committed calculation snapshot to explain."""


class AiExplanationUnavailable(RuntimeError):
    """Raised when an explanation request cannot produce accepted AI output."""


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
            logger.warning("AI explanation unavailable: stored response failed contract validation")
            raise AiExplanationUnavailable from None
        return AiExplanationResult(
            snapshot=snapshot,
            response=response,
            source=AiExplanationSource.GENERATED,
            explanation=stored,
        )

    if not settings.ai_summary_enabled:
        logger.info("AI explanation unavailable: feature is disabled")
        raise AiExplanationUnavailable

    try:
        snapshot_result = parse_snapshot_result(snapshot.result_json)
        payload = build_ai_payload(snapshot_result)
        if provider is None:
            logger.warning("AI explanation unavailable: provider is not configured")
            raise AiExplanationUnavailable
        raw_response = provider.generate(
            payload=payload,
            timeout_seconds=settings.ai_summary_timeout_seconds,
        )
        response = validate_ai_response(raw_response)
    except AiProviderError as exc:
        logger.warning("AI explanation unavailable: provider failure (%s)", type(exc).__name__)
        raise AiExplanationUnavailable from exc
    except SnapshotContractError:
        logger.warning("AI explanation unavailable: snapshot failed contract validation")
        raise AiExplanationUnavailable from None
    except AiContractError:
        logger.warning("AI explanation unavailable: provider response failed contract validation")
        raise AiExplanationUnavailable from None

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
