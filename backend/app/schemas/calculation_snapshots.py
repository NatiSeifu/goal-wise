"""Calculation snapshot API schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CalculationSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    goal_id: str
    formula_version: str
    trigger: str
    normalized_input_json: dict[str, Any]
    result_json: dict[str, Any]
    calculated_at: datetime
    created_at: datetime


class CalculationSnapshotItemResponse(BaseModel):
    item: CalculationSnapshotResponse | None
