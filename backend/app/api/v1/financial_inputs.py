"""Financial input API routes."""

from datetime import UTC, datetime

from fastapi import APIRouter, Response

from app.api.dependencies import CsrfSessionDep, CurrentSessionDep, DbSessionDep
from app.api.errors import error_response, validation_error_response
from app.models import FinancialProfile, IncomeSource, PlannedExpense
from app.schemas.financial_inputs import (
    FinancialProfileItemResponse,
    FinancialProfileRequest,
    FinancialProfileResponse,
    IncomeSourceItemResponse,
    IncomeSourceListResponse,
    IncomeSourceRequest,
    IncomeSourceResponse,
    PlannedExpenseItemResponse,
    PlannedExpenseListResponse,
    PlannedExpenseRequest,
    PlannedExpenseResponse,
)
from app.services.financial_inputs import (
    FinancialInputNotFoundError,
    FinancialInputValidationError,
    create_income_source_for_user,
    create_planned_expense_for_user,
    deactivate_income_source_for_user,
    deactivate_planned_expense_for_user,
    get_financial_profile_for_user,
    list_income_sources_for_user,
    list_planned_expenses_for_user,
    update_income_source_for_user,
    update_planned_expense_for_user,
    upsert_financial_profile_for_user,
)

profile_router = APIRouter(prefix="/financial-profile", tags=["financial-profile"])
income_router = APIRouter(prefix="/income-sources", tags=["income-sources"])
expense_router = APIRouter(prefix="/planned-expenses", tags=["planned-expenses"])


@profile_router.get("", response_model=FinancialProfileItemResponse)
def get_financial_profile(
    current_session: CurrentSessionDep,
    db_session: DbSessionDep,
) -> FinancialProfileItemResponse:
    profile = get_financial_profile_for_user(
        db_session,
        user_id=current_session.user.id,
    )
    return FinancialProfileItemResponse(item=_financial_profile_response(profile))


@profile_router.put("", response_model=FinancialProfileItemResponse)
def put_financial_profile(
    payload: FinancialProfileRequest,
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
) -> FinancialProfileItemResponse | Response:
    try:
        profile = upsert_financial_profile_for_user(
            db_session,
            user_id=current_session.user.id,
            starting_cash_cents=payload.starting_cash_cents,
            balance_as_of_date=payload.balance_as_of_date,
            reserve_buffer_cents=payload.reserve_buffer_cents,
            reserve_buffer_confirmed=payload.reserve_buffer_confirmed,
            user_time_zone=current_session.user.time_zone,
            now=_utc_now(),
        )
    except FinancialInputValidationError as exc:
        db_session.rollback()
        return validation_error_response(fields=exc.fields)

    db_session.commit()
    return FinancialProfileItemResponse(item=_financial_profile_response(profile))


@income_router.get("", response_model=IncomeSourceListResponse)
def list_income_sources(
    current_session: CurrentSessionDep,
    db_session: DbSessionDep,
) -> IncomeSourceListResponse:
    income_sources = list_income_sources_for_user(
        db_session,
        user_id=current_session.user.id,
    )
    return IncomeSourceListResponse(
        items=[_income_source_response(income_source) for income_source in income_sources],
    )


@income_router.post("", response_model=IncomeSourceItemResponse, status_code=201)
def create_income_source(
    payload: IncomeSourceRequest,
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
) -> IncomeSourceItemResponse | Response:
    try:
        income_source = create_income_source_for_user(
            db_session,
            user_id=current_session.user.id,
            name=payload.name,
            amount_cents=payload.amount_cents,
            next_date=payload.next_date,
            frequency=payload.frequency,
            confidence=payload.confidence,
        )
    except FinancialInputValidationError as exc:
        db_session.rollback()
        return validation_error_response(fields=exc.fields)

    db_session.commit()
    return IncomeSourceItemResponse(item=_income_source_response(income_source))


@income_router.patch("/{income_source_id}", response_model=IncomeSourceItemResponse)
def update_income_source(
    income_source_id: str,
    payload: IncomeSourceRequest,
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
) -> IncomeSourceItemResponse | Response:
    try:
        income_source = update_income_source_for_user(
            db_session,
            user_id=current_session.user.id,
            income_source_id=income_source_id,
            name=payload.name,
            amount_cents=payload.amount_cents,
            next_date=payload.next_date,
            frequency=payload.frequency,
            confidence=payload.confidence,
        )
    except FinancialInputNotFoundError:
        db_session.rollback()
        return _not_found("Income source not found.")
    except FinancialInputValidationError as exc:
        db_session.rollback()
        return validation_error_response(fields=exc.fields)

    db_session.commit()
    return IncomeSourceItemResponse(item=_income_source_response(income_source))


@income_router.delete("/{income_source_id}", status_code=204)
def delete_income_source(
    income_source_id: str,
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
) -> Response:
    try:
        deactivate_income_source_for_user(
            db_session,
            user_id=current_session.user.id,
            income_source_id=income_source_id,
        )
    except FinancialInputNotFoundError:
        db_session.rollback()
        return _not_found("Income source not found.")

    db_session.commit()
    return Response(status_code=204)


@expense_router.get("", response_model=PlannedExpenseListResponse)
def list_planned_expenses(
    current_session: CurrentSessionDep,
    db_session: DbSessionDep,
) -> PlannedExpenseListResponse:
    planned_expenses = list_planned_expenses_for_user(
        db_session,
        user_id=current_session.user.id,
    )
    return PlannedExpenseListResponse(
        items=[
            _planned_expense_response(planned_expense)
            for planned_expense in planned_expenses
        ],
    )


@expense_router.post("", response_model=PlannedExpenseItemResponse, status_code=201)
def create_planned_expense(
    payload: PlannedExpenseRequest,
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
) -> PlannedExpenseItemResponse | Response:
    try:
        planned_expense = create_planned_expense_for_user(
            db_session,
            user_id=current_session.user.id,
            name=payload.name,
            amount_cents=payload.amount_cents,
            next_date=payload.next_date,
            frequency=payload.frequency,
            classification=payload.classification,
        )
    except FinancialInputValidationError as exc:
        db_session.rollback()
        return validation_error_response(fields=exc.fields)

    db_session.commit()
    return PlannedExpenseItemResponse(item=_planned_expense_response(planned_expense))


@expense_router.patch("/{planned_expense_id}", response_model=PlannedExpenseItemResponse)
def update_planned_expense(
    planned_expense_id: str,
    payload: PlannedExpenseRequest,
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
) -> PlannedExpenseItemResponse | Response:
    try:
        planned_expense = update_planned_expense_for_user(
            db_session,
            user_id=current_session.user.id,
            planned_expense_id=planned_expense_id,
            name=payload.name,
            amount_cents=payload.amount_cents,
            next_date=payload.next_date,
            frequency=payload.frequency,
            classification=payload.classification,
        )
    except FinancialInputNotFoundError:
        db_session.rollback()
        return _not_found("Planned expense not found.")
    except FinancialInputValidationError as exc:
        db_session.rollback()
        return validation_error_response(fields=exc.fields)

    db_session.commit()
    return PlannedExpenseItemResponse(item=_planned_expense_response(planned_expense))


@expense_router.delete("/{planned_expense_id}", status_code=204)
def delete_planned_expense(
    planned_expense_id: str,
    current_session: CsrfSessionDep,
    db_session: DbSessionDep,
) -> Response:
    try:
        deactivate_planned_expense_for_user(
            db_session,
            user_id=current_session.user.id,
            planned_expense_id=planned_expense_id,
        )
    except FinancialInputNotFoundError:
        db_session.rollback()
        return _not_found("Planned expense not found.")

    db_session.commit()
    return Response(status_code=204)


def _not_found(message: str) -> Response:
    return error_response(
        status_code=404,
        code="not_found",
        message=message,
    )


def _financial_profile_response(
    profile: FinancialProfile | None,
) -> FinancialProfileResponse | None:
    if profile is None:
        return None
    return FinancialProfileResponse.model_validate(profile)


def _income_source_response(income_source: IncomeSource) -> IncomeSourceResponse:
    return IncomeSourceResponse.model_validate(income_source)


def _planned_expense_response(planned_expense: PlannedExpense) -> PlannedExpenseResponse:
    return PlannedExpenseResponse.model_validate(planned_expense)


def _utc_now() -> datetime:
    return datetime.now(UTC)
