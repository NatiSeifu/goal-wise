from __future__ import annotations

import pytest
from app.pace_engine import calculate_pace
from app.pace_engine.calculator import suggest_reserve_buffer_cents

from tests.pace_engine.fixtures import (
    GOLDEN_SCENARIOS,
    RESERVE_BUFFER_SUGGESTION_EXAMPLES,
    GoldenScenario,
)


@pytest.mark.parametrize(
    "scenario",
    GOLDEN_SCENARIOS,
    ids=[scenario.name for scenario in GOLDEN_SCENARIOS],
)
def test_golden_scenarios_match_expected_results(scenario: GoldenScenario) -> None:
    assert calculate_pace(scenario.input_data) == scenario.expected_result


@pytest.mark.parametrize(
    ("confirmed_future_income_cents", "expected"),
    RESERVE_BUFFER_SUGGESTION_EXAMPLES,
    ids=[
        "zero-income",
        "five-percent-exact-dollar",
        "five-percent-rounds-up",
        "one-cent-rounds-up",
    ],
)
def test_reserve_buffer_suggestion_golden_examples(
    confirmed_future_income_cents: int, expected: int
) -> None:
    assert suggest_reserve_buffer_cents(confirmed_future_income_cents) == expected


def test_calculate_pace_is_deterministic() -> None:
    scenario = GOLDEN_SCENARIOS[4]

    assert calculate_pace(scenario.input_data) == calculate_pace(scenario.input_data)
