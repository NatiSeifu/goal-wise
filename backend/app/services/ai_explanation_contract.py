"""Validated contracts for optional AI explanation requests and responses."""

import re
from collections.abc import Mapping
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from app.schemas.snapshots import SnapshotResultV1

AI_EXPLANATION_SCHEMA_VERSION = "ai-explanation-v2"

PaceMetric = Literal[
    "pace_status",
    "weekly_safe_to_spend_cents",
    "projected_shortfall_cents",
    "progress_percentage",
    "remaining_weeks",
    "formula_version",
]
ObservationKind = Literal["pace", "allowance", "progress", "shortfall"]
ObservationTone = Literal["positive", "neutral", "caution"]

_PROHIBITED_TERMS = (
    "investment",
    "investing",
    "lending",
    "loan",
    "tax advice",
    "legal advice",
    "automatic transfer",
    "automatically",
    "transfer money",
)
_NUMERIC_TEXT_PATTERN = re.compile(r"[\d$€£%]")


class AiContractError(ValueError):
    """Raised when an AI payload or response violates the application contract."""


class AiSummaryPayload(BaseModel):
    """The only snapshot values permitted in the provider request."""

    model_config = ConfigDict(extra="forbid")

    pace_status: str = Field(min_length=1, max_length=32)
    weekly_safe_to_spend_cents: int = Field(ge=0)
    projected_shortfall_cents: int = Field(ge=0)
    progress_percentage: float = Field(ge=0, le=100)
    remaining_weeks: int = Field(ge=1)
    formula_version: str = Field(min_length=1, max_length=32)


def _validate_prose(value: str) -> str:
    lowered = value.casefold()
    if _NUMERIC_TEXT_PATTERN.search(value) is not None:
        raise ValueError("generated prose must not contain numeric values")
    if any(term in lowered for term in _PROHIBITED_TERMS):
        raise ValueError("generated prose contains prohibited advice")
    return value


class AiObservation(BaseModel):
    """A substantive observation with evidence from the committed snapshot."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    kind: ObservationKind
    tone: ObservationTone
    text: str = Field(min_length=80, max_length=450)
    metric_refs: list[PaceMetric] = Field(min_length=1, max_length=3)

    @field_validator("text")
    @classmethod
    def reject_unsafe_text(cls, value: str) -> str:
        return _validate_prose(value)

    @model_validator(mode="after")
    def require_relevant_evidence(self) -> Self:
        primary_metrics = {
            "pace": "pace_status",
            "allowance": "weekly_safe_to_spend_cents",
            "progress": "progress_percentage",
            "shortfall": "projected_shortfall_cents",
        }
        if primary_metrics[self.kind] not in self.metric_refs:
            raise ValueError("observation must reference its primary metric")
        if len(set(self.metric_refs)) != len(self.metric_refs):
            raise ValueError("metric references must be distinct")
        return self


class AiExplanationResponse(BaseModel):
    """Validated, bounded digest; financial values remain snapshot-owned."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    schema_version: Literal["ai-explanation-v2"]
    headline: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=80, max_length=600)
    observations: list[AiObservation] = Field(min_length=2, max_length=3)
    next_step: str = Field(min_length=40, max_length=360)
    next_step_action: Literal["review_goal", "review_inputs"]

    @field_validator("headline", "body", "next_step")
    @classmethod
    def reject_unsafe_text(cls, value: str) -> str:
        return _validate_prose(value)

    @model_validator(mode="after")
    def require_bounded_depth(self) -> Self:
        kinds = [item.kind for item in self.observations]
        if len(set(kinds)) != len(kinds):
            raise ValueError("observation topics must be distinct")
        prose = " ".join(
            [
                self.headline,
                self.body,
                self.next_step,
                *(item.text for item in self.observations),
            ]
        )
        if not 90 <= len(prose.split()) <= 240:
            raise ValueError("digest must contain between ninety and two hundred forty words")
        return self


def build_ai_payload(result: SnapshotResultV1) -> dict[str, object]:
    """Extract and validate the allowlisted fields from a snapshot result."""

    raw_payload = {
        "pace_status": result.outputs.pace_status,
        "weekly_safe_to_spend_cents": result.outputs.weekly_safe_to_spend_cents,
        "projected_shortfall_cents": result.outputs.projected_shortfall_cents,
        "progress_percentage": result.outputs.progress_percentage,
        "remaining_weeks": result.outputs.remaining_weeks,
        "formula_version": result.formula_version,
    }
    try:
        return AiSummaryPayload.model_validate(raw_payload).model_dump()
    except ValidationError as exc:
        raise AiContractError("AI payload failed contract validation.") from exc


def validate_ai_response(raw_response: Mapping[str, object]) -> AiExplanationResponse:
    """Validate untrusted provider JSON before it reaches persistence or UI."""

    try:
        return AiExplanationResponse.model_validate(raw_response)
    except ValidationError as exc:
        raise AiContractError("AI response failed contract validation.") from exc
