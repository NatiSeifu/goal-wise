"""API schemas for user-facing snapshot explanations."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.services.ai_explanation_contract import AiExplanationResponse


class AIExplanationItem(BaseModel):
    snapshot_id: str
    calculated_at: datetime
    formula_version: str
    source: Literal["generated", "fallback"]
    explanation: AiExplanationResponse


class AIExplanationItemResponse(BaseModel):
    item: AIExplanationItem
