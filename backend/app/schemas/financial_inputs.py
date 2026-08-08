"""Financial input API schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class FinancialProfileRequest(BaseModel):
    starting_cash_cents: int
    balance_as_of_date: date
    reserve_buffer_cents: int
    reserve_buffer_confirmed: bool


class FinancialProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    starting_cash_cents: int
    balance_as_of_date: date
    reserve_buffer_cents: int
    reserve_buffer_confirmed: bool
    created_at: datetime
    updated_at: datetime


class FinancialProfileItemResponse(BaseModel):
    item: FinancialProfileResponse | None


class IncomeSourceRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    amount_cents: int
    next_date: date
    frequency: str
    confidence: str


class IncomeSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    amount_cents: int
    next_date: date
    frequency: str
    confidence: str
    active: bool
    created_at: datetime
    updated_at: datetime


class IncomeSourceItemResponse(BaseModel):
    item: IncomeSourceResponse


class IncomeSourceListResponse(BaseModel):
    items: list[IncomeSourceResponse]


class PlannedExpenseRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    amount_cents: int
    next_date: date
    frequency: str
    classification: str


class PlannedExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    amount_cents: int
    next_date: date
    frequency: str
    classification: str
    active: bool
    created_at: datetime
    updated_at: datetime


class PlannedExpenseItemResponse(BaseModel):
    item: PlannedExpenseResponse


class PlannedExpenseListResponse(BaseModel):
    items: list[PlannedExpenseResponse]
