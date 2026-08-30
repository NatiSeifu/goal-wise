"""Validated contracts for optional AI explanation requests and responses."""

import re
from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

AI_EXPLANATION_SCHEMA_VERSION = "ai-explanation-v1"

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


class AiObservation(BaseModel):
    """A natural-language observation linked to trusted snapshot metrics."""

    model_config = ConfigDict(extra="forbid")

    kind: ObservationKind
    tone: ObservationTone
    metric_refs: list[PaceMetric] = Field(default_factory=list, max_length=4)


class AiExplanationResponse(BaseModel):
    """Validated provider output safe for user-facing rendering."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["ai-explanation-v1"]
    headline: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=800)
    observations: list[AiObservation] = Field(max_length=4)
    next_step: str | None = Field(default=None, max_length=240)

    @field_validator("headline", "body", "next_step")
    @classmethod
    def reject_unsafe_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        lowered = value.casefold()
        if _NUMERIC_TEXT_PATTERN.search(value) is not None:
            raise ValueError("generated prose must not contain numeric values")
        if any(term in lowered for term in _PROHIBITED_TERMS):
            raise ValueError("generated prose contains prohibited advice")
        return value


def build_ai_payload(result_json: Mapping[str, object]) -> dict[str, object]:
    """Extract and validate the allowlisted fields from a snapshot result."""

    outputs = result_json.get("outputs")
    formula_version = result_json.get("formula_version")
    if not isinstance(outputs, Mapping):
        raise AiContractError("AI payload is missing outputs.")

    raw_payload = {
        "pace_status": outputs.get("pace_status"),
        "weekly_safe_to_spend_cents": outputs.get("weekly_safe_to_spend_cents"),
        "projected_shortfall_cents": outputs.get("projected_shortfall_cents"),
        "progress_percentage": outputs.get("progress_percentage"),
        "remaining_weeks": outputs.get("remaining_weeks"),
        "formula_version": formula_version,
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
