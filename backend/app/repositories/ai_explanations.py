"""AI explanation persistence queries."""

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AIExplanation


def create_ai_explanation(
    db_session: Session,
    *,
    user_id: str,
    snapshot_id: str,
    provider: str,
    model: str,
    prompt_version: str,
    response_schema_version: str,
    response_json: Mapping[str, Any],
    generated_at: datetime,
) -> AIExplanation:
    explanation = AIExplanation(
        user_id=user_id,
        snapshot_id=snapshot_id,
        provider=provider,
        model=model,
        prompt_version=prompt_version,
        response_schema_version=response_schema_version,
        response_json=dict(response_json),
        generated_at=generated_at,
    )
    db_session.add(explanation)
    db_session.flush()
    return explanation


def get_ai_explanation_for_version(
    db_session: Session,
    *,
    user_id: str,
    snapshot_id: str,
    provider: str,
    model: str,
    prompt_version: str,
    response_schema_version: str,
) -> AIExplanation | None:
    return db_session.scalar(
        select(AIExplanation).where(
            AIExplanation.user_id == user_id,
            AIExplanation.snapshot_id == snapshot_id,
            AIExplanation.provider == provider,
            AIExplanation.model == model,
            AIExplanation.prompt_version == prompt_version,
            AIExplanation.response_schema_version == response_schema_version,
        )
    )
