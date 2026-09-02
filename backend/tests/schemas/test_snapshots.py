import pytest
from app.schemas.snapshots import (
    SnapshotContractError,
    SnapshotInputV1,
    SnapshotResultV1,
    parse_snapshot_input,
    parse_snapshot_result,
)
from pydantic import ValidationError


def _input_document() -> dict[str, object]:
    return {
        "schema_version": "snapshot-input-v1",
        "formula_version": "pace-v1",
        "calculation": {
            "timestamp_utc": "2026-08-01T17:00:00Z",
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
            "balance_as_of_date": "2026-08-01",
            "reserve_buffer_cents": 5000,
            "reserve_buffer_confirmed": True,
        },
        "income_sources": [],
        "planned_expenses": [],
        "transactions": [],
    }


def _result_document() -> dict[str, object]:
    return {
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


def test_snapshot_input_v1_accepts_spec_shape() -> None:
    document = SnapshotInputV1.model_validate(_input_document())

    assert document.goal.current_saved_cents == 75000
    assert document.calculation.timestamp_utc.isoformat() == "2026-08-01T17:00:00+00:00"


def test_snapshot_result_v1_accepts_spec_shape() -> None:
    document = SnapshotResultV1.model_validate(_result_document())

    assert document.outputs.weekly_safe_to_spend_cents == 15400
    assert document.changed_from_previous.previous_snapshot_id is None


@pytest.mark.parametrize(
    "mutate",
    [
        lambda document: document.update(schema_version="snapshot-input-v2"),
        lambda document: document["goal"].update(target_cents=3000.5),
        lambda document: document["goal"].pop("target_date"),
        lambda document: document.update(unexpected_field=True),
    ],
)
def test_snapshot_input_v1_rejects_invalid_documents(mutate) -> None:
    document = _input_document()
    mutate(document)

    with pytest.raises(ValidationError):
        SnapshotInputV1.model_validate(document)


def test_snapshot_result_v1_rejects_unknown_status_and_extra_fields() -> None:
    document = _result_document()
    document["outputs"]["pace_status"] = "Needs attention"
    document["extra"] = "not allowed"

    with pytest.raises(ValidationError):
        SnapshotResultV1.model_validate(document)


def test_snapshot_models_dump_json_compatible_documents() -> None:
    input_document = SnapshotInputV1.model_validate(_input_document())
    result_document = SnapshotResultV1.model_validate(_result_document())

    assert input_document.model_dump(mode="json")["calculation"]["timestamp_utc"] == (
        "2026-08-01T17:00:00Z"
    )
    assert result_document.model_dump(mode="json")["outputs"]["pace_status"] == "On Track"


def test_snapshot_parsers_return_typed_documents() -> None:
    input_document = parse_snapshot_input(_input_document())
    result_document = parse_snapshot_result(_result_document())

    assert isinstance(input_document, SnapshotInputV1)
    assert isinstance(result_document, SnapshotResultV1)


def test_snapshot_parsers_normalize_validation_failures() -> None:
    invalid_result = _result_document()
    invalid_result["schema_version"] = "snapshot-result-v2"

    with pytest.raises(SnapshotContractError, match="result failed contract"):
        parse_snapshot_result(invalid_result)
