from datetime import UTC, date, datetime

from app.models import (
    CalculationSnapshot,
    FinancialProfile,
    Goal,
    IncomeSource,
    PlannedExpense,
)
from app.pace_engine.types import FORMULA_VERSION, PaceResult, PaceStatus
from app.services.snapshot_json import build_snapshot_json


def test_build_snapshot_json_matches_required_input_shape() -> None:
    goal = _goal()
    profile = _profile()
    income = _income_source(confidence="confirmed")
    expense = _planned_expense()

    payload = build_snapshot_json(
        trigger="goal_updated",
        calculated_at=_calculated_at(),
        user_time_zone="America/Los_Angeles",
        goal=goal,
        financial_profile=profile,
        income_sources=(income,),
        planned_expenses=(expense,),
        pace_result=_pace_result(),
        previous_snapshot=None,
    )

    assert payload.normalized_input_json == {
        "schema_version": "snapshot-input-v1",
        "formula_version": "pace-v1",
        "calculation": {
            "timestamp_utc": "2026-08-08T12:00:00Z",
            "user_time_zone": "America/Los_Angeles",
            "trigger": "goal_updated",
        },
        "goal": {
            "id": "goal-1",
            "name": "Emergency fund",
            "target_cents": 300000,
            "initial_saved_cents": 50000,
            "current_saved_cents": 75000,
            "start_date": "2026-08-01",
            "target_date": "2026-12-31",
            "status": "active",
        },
        "financial_profile": {
            "starting_cash_cents": 120000,
            "balance_as_of_date": "2026-08-07",
            "reserve_buffer_cents": 5000,
            "reserve_buffer_confirmed": True,
        },
        "income_sources": [
            {
                "id": "income-1",
                "name": "Campus job",
                "amount_cents": 45000,
                "next_date": "2026-08-14",
                "frequency": "weekly",
                "confidence": "confirmed",
                "active": True,
            }
        ],
        "planned_expenses": [
            {
                "id": "expense-1",
                "name": "Rent",
                "amount_cents": 90000,
                "next_date": "2026-09-01",
                "frequency": "monthly",
                "classification": "essential",
                "active": True,
            }
        ],
        "transactions": [],
    }


def test_build_snapshot_json_matches_required_result_shape() -> None:
    payload = build_snapshot_json(
        trigger="income_source_updated",
        calculated_at=_calculated_at(),
        user_time_zone="America/Los_Angeles",
        goal=_goal(),
        financial_profile=_profile(),
        income_sources=(
            _income_source(id="income-1", confidence="confirmed"),
            _income_source(id="income-2", confidence="unconfirmed"),
        ),
        planned_expenses=(_planned_expense(),),
        pace_result=_pace_result(),
        previous_snapshot=None,
    )

    assert payload.result_json == {
        "schema_version": "snapshot-result-v1",
        "formula_version": "pace-v1",
        "outputs": {
            "current_cash_cents": 120000,
            "confirmed_future_income_cents": 900000,
            "planned_future_expenses_cents": 450000,
            "reserve_buffer_cents": 5000,
            "forecast_resources_cents": 565000,
            "goal_gap_cents": 225000,
            "discretionary_capacity_cents": 340000,
            "remaining_weeks": 22,
            "weekly_safe_to_spend_cents": 15400,
            "projected_shortfall_cents": 0,
            "expected_savings_to_date_cents": 75000,
            "pace_status": "On Track",
            "progress_percentage": 25.0,
            "current_week_opening_allowance_cents": 15400,
            "current_week_remainder_cents": 15400,
        },
        "explanation": {
            "included_income_source_ids": ["income-1"],
            "excluded_income_source_ids": ["income-2"],
            "included_planned_expense_ids": ["expense-1"],
            "excluded_planned_expense_ids": [],
            "summary": {
                "confirmed_income_count": 1,
                "planned_expense_count": 1,
                "unconfirmed_income_count": 1,
            },
        },
        "changed_from_previous": {
            "previous_snapshot_id": None,
            "changed_input_categories": [],
            "weekly_safe_to_spend_delta_cents": None,
        },
    }


def test_build_snapshot_json_compares_previous_snapshot() -> None:
    previous_snapshot = CalculationSnapshot(
        id="snapshot-1",
        user_id="user-1",
        goal_id="goal-1",
        formula_version=FORMULA_VERSION,
        trigger="goal_updated",
        normalized_input_json={
            "schema_version": "snapshot-input-v1",
            "goal": {"id": "goal-1", "name": "Old name"},
            "financial_profile": {
                "starting_cash_cents": 120000,
                "balance_as_of_date": "2026-08-07",
                "reserve_buffer_cents": 5000,
                "reserve_buffer_confirmed": True,
            },
            "income_sources": [],
            "planned_expenses": [],
            "transactions": [],
        },
        result_json={
            "schema_version": "snapshot-result-v1",
            "outputs": {"weekly_safe_to_spend_cents": 15000},
        },
        calculated_at=_calculated_at(),
    )

    payload = build_snapshot_json(
        trigger="goal_updated",
        calculated_at=_calculated_at(),
        user_time_zone="America/Los_Angeles",
        goal=_goal(),
        financial_profile=_profile(),
        income_sources=(),
        planned_expenses=(),
        pace_result=_pace_result(),
        previous_snapshot=previous_snapshot,
    )

    assert payload.result_json["changed_from_previous"] == {
        "previous_snapshot_id": "snapshot-1",
        "changed_input_categories": ["goal"],
        "weekly_safe_to_spend_delta_cents": 400,
    }


def test_snapshot_json_does_not_include_raw_transaction_descriptions() -> None:
    payload = build_snapshot_json(
        trigger="dashboard_opened",
        calculated_at=_calculated_at(),
        user_time_zone="America/Los_Angeles",
        goal=_goal(),
        financial_profile=_profile(),
        income_sources=(),
        planned_expenses=(),
        pace_result=_pace_result(),
        previous_snapshot=None,
    )

    assert payload.normalized_input_json["transactions"] == []
    assert "description" not in str(payload.normalized_input_json["transactions"])
    assert "raw_description" not in str(payload.normalized_input_json["transactions"])


def _goal() -> Goal:
    return Goal(
        id="goal-1",
        user_id="user-1",
        name="Emergency fund",
        target_cents=300000,
        initial_saved_cents=50000,
        current_saved_cents=75000,
        start_date=date(2026, 8, 1),
        target_date=date(2026, 12, 31),
        status="active",
    )


def _profile() -> FinancialProfile:
    return FinancialProfile(
        id="profile-1",
        user_id="user-1",
        starting_cash_cents=120000,
        balance_as_of_date=date(2026, 8, 7),
        reserve_buffer_cents=5000,
        reserve_buffer_confirmed=True,
    )


def _income_source(
    *,
    id: str = "income-1",
    confidence: str = "confirmed",
) -> IncomeSource:
    return IncomeSource(
        id=id,
        user_id="user-1",
        name="Campus job",
        amount_cents=45000,
        next_date=date(2026, 8, 14),
        frequency="weekly",
        confidence=confidence,
        active=True,
    )


def _planned_expense() -> PlannedExpense:
    return PlannedExpense(
        id="expense-1",
        user_id="user-1",
        name="Rent",
        amount_cents=90000,
        next_date=date(2026, 9, 1),
        frequency="monthly",
        classification="essential",
        active=True,
    )


def _pace_result() -> PaceResult:
    return PaceResult(
        formula_version=FORMULA_VERSION,
        current_cash_cents=120000,
        confirmed_future_income_cents=900000,
        planned_future_expenses_cents=450000,
        reserve_buffer_cents=5000,
        forecast_resources_cents=565000,
        goal_gap_cents=225000,
        discretionary_capacity_cents=340000,
        remaining_weeks=22,
        weekly_safe_to_spend_cents=15400,
        projected_shortfall_cents=0,
        expected_savings_to_date_cents=75000,
        pace_status=PaceStatus.ON_TRACK,
    )


def _calculated_at() -> datetime:
    return datetime(2026, 8, 8, 12, 0, tzinfo=UTC)
