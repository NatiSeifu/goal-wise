"""Goal input API schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class GoalRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    target_cents: int
    initial_saved_cents: int
    current_saved_cents: int
    start_date: date
    target_date: date


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    target_cents: int
    initial_saved_cents: int
    current_saved_cents: int
    start_date: date
    target_date: date
    status: str
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class GoalItemResponse(BaseModel):
    item: GoalResponse | None
