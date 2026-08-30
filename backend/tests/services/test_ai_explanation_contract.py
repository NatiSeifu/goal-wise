import pytest
from app.schemas.snapshots import parse_snapshot_result
from app.services.ai_explanation_contract import (
    AiContractError,
    build_ai_payload,
    validate_ai_response,
)


def test_build_ai_payload_allowlists_snapshot_outputs() -> None:
    result_json = {
        "schema_version": "snapshot-result-v1",
        "formula_version": "pace-v1",
        "outputs": {
            "current_cash_cents": 220000,
            "confirmed_future_income_cents": 100000,
            "planned_future_expenses_cents": 50000,
            "reserve_buffer_cents": 10000,
            "forecast_resources_cents": 260000,
            "goal_gap_cents": 80000,
            "discretionary_capacity_cents": 90000,
            "pace_status": "On Track",
            "weekly_safe_to_spend_cents": 81800,
            "projected_shortfall_cents": 0,
            "progress_percentage": 28.0,
            "remaining_weeks": 16,
            "expected_savings_to_date_cents": 84000,
            "current_week_opening_allowance_cents": 81800,
            "current_week_remainder_cents": 81800,
        },
        "explanation": {
            "included_income_source_ids": [],
            "excluded_income_source_ids": [],
            "included_planned_expense_ids": [],
            "excluded_planned_expense_ids": [],
            "summary": {
                "confirmed_income_count": 0,
                "planned_expense_count": 0,
                "unconfirmed_income_count": 0,
            },
        },
        "changed_from_previous": {
            "previous_snapshot_id": None,
            "changed_input_categories": [],
            "weekly_safe_to_spend_delta_cents": None,
        },
    }

    payload = build_ai_payload(parse_snapshot_result(result_json))

    assert payload == {
        "pace_status": "On Track",
        "weekly_safe_to_spend_cents": 81800,
        "projected_shortfall_cents": 0,
        "progress_percentage": 28.0,
        "remaining_weeks": 16,
        "formula_version": "pace-v1",
    }
    assert "current_cash_cents" not in payload
    assert "goal" not in payload


def test_build_ai_payload_rejects_missing_outputs() -> None:
    with pytest.raises(ValueError, match="result failed contract"):
        parse_snapshot_result({})


def test_validate_ai_response_accepts_natural_language_without_numbers() -> None:
    response = validate_ai_response(
        {
            "schema_version": "ai-explanation-v1",
            "headline": "Your plan is on track",
            "body": (
                "Your current plan leaves room for weekly spending while keeping the goal in view."
            ),
            "observations": [
                {
                    "kind": "pace",
                    "tone": "positive",
                    "metric_refs": ["pace_status", "weekly_safe_to_spend_cents"],
                }
            ],
            "next_step": "Keep your planned expenses up to date.",
        }
    )

    assert response.schema_version == "ai-explanation-v1"
    assert response.observations[0].metric_refs == [
        "pace_status",
        "weekly_safe_to_spend_cents",
    ]


@pytest.mark.parametrize(
    "body",
    [
        "You can spend $818 this week.",
        "Consider investing the available money.",
        "Transfer money automatically to stay on track.",
    ],
)
def test_validate_ai_response_rejects_numeric_or_prohibited_text(body: str) -> None:
    with pytest.raises(AiContractError):
        validate_ai_response(
            {
                "schema_version": "ai-explanation-v1",
                "headline": "Plan summary",
                "body": body,
                "observations": [],
                "next_step": None,
            }
        )


def test_validate_ai_response_rejects_unknown_fields_and_metrics() -> None:
    with pytest.raises(AiContractError):
        validate_ai_response(
            {
                "schema_version": "ai-explanation-v1",
                "headline": "Plan summary",
                "body": "Your plan has been reviewed.",
                "observations": [
                    {
                        "kind": "pace",
                        "tone": "neutral",
                        "metric_refs": ["private_goal_name"],
                    }
                ],
                "next_step": None,
                "provider_raw_text": "must not be accepted",
            }
        )
