from datetime import UTC, datetime, timedelta

import pytest
from app.pace_engine import (
    ExpenseClassification,
    IncomeConfidence,
    IncomeSourceInput,
    PlannedExpenseInput,
    RecurrenceFrequency,
)
from app.services.planning_import import PlanningImport, PlanningImportCash, PlanningImportGoal
from app.services.planning_import_tokens import (
    InvalidPlanningImportToken,
    create_planning_import_token,
    read_planning_import_token,
)
from pydantic import SecretStr


def test_preview_token_round_trips_normalized_plan() -> None:
    planning_import = PlanningImport(
        goal=PlanningImportGoal(
            name="Moving fund",
            target_cents=300_000,
            initial_saved_cents=50_000,
            current_saved_cents=75_000,
            start_date=datetime(2026, 8, 1, tzinfo=UTC).date(),
            target_date=datetime(2026, 11, 15, tzinfo=UTC).date(),
        ),
        cash=PlanningImportCash(
            starting_cash_cents=200_000,
            balance_as_of_date=datetime(2026, 8, 27, tzinfo=UTC).date(),
            reserve_buffer_cents=30_000,
        ),
        income_sources=(
            IncomeSourceInput(
                name="Salary",
                amount_cents=250_000,
                next_date=datetime(2026, 9, 1, tzinfo=UTC).date(),
                frequency=RecurrenceFrequency.BIWEEKLY,
                confidence=IncomeConfidence.CONFIRMED,
            ),
        ),
        planned_expenses=(
            PlannedExpenseInput(
                name="Rent",
                amount_cents=140_000,
                next_date=datetime(2026, 9, 1, tzinfo=UTC).date(),
                frequency=RecurrenceFrequency.MONTHLY,
                classification=ExpenseClassification.ESSENTIAL,
            ),
        ),
    )
    issued_at = datetime(2026, 8, 27, 12, tzinfo=UTC)

    token = create_planning_import_token(
        planning_import,
        user_id="user-1",
        session_secret=SecretStr("test-secret"),
        issued_at=issued_at,
    )

    assert (
        read_planning_import_token(
            token,
            user_id="user-1",
            session_secret=SecretStr("test-secret"),
            now=issued_at + timedelta(minutes=14),
        )
        == planning_import
    )


@pytest.mark.parametrize(
    ("user_id", "now"),
    [
        ("other-user", datetime(2026, 8, 27, 12, tzinfo=UTC)),
        ("user-1", datetime(2026, 8, 27, 12, 16, tzinfo=UTC)),
    ],
)
def test_preview_token_rejects_wrong_user_or_expiry(
    user_id: str,
    now: datetime,
) -> None:
    issued_at = datetime(2026, 8, 27, 12, tzinfo=UTC)
    token = create_planning_import_token(
        _minimal_import(),
        user_id="user-1",
        session_secret="test-secret",
        issued_at=issued_at,
    )

    with pytest.raises(InvalidPlanningImportToken):
        read_planning_import_token(
            token,
            user_id=user_id,
            session_secret="test-secret",
            now=now,
        )


def _minimal_import() -> PlanningImport:
    return PlanningImport(
        goal=PlanningImportGoal(
            name="Goal",
            target_cents=100,
            initial_saved_cents=0,
            current_saved_cents=0,
            start_date=datetime(2026, 8, 1, tzinfo=UTC).date(),
            target_date=datetime(2026, 9, 1, tzinfo=UTC).date(),
        ),
        cash=PlanningImportCash(
            starting_cash_cents=0,
            balance_as_of_date=datetime(2026, 8, 27, tzinfo=UTC).date(),
            reserve_buffer_cents=0,
        ),
        income_sources=(),
        planned_expenses=(),
    )
