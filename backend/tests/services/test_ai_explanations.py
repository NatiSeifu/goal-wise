from datetime import UTC, datetime, timedelta

import pytest
from app.core.config import Settings
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.models import AIExplanation, CalculationSnapshot, User
from app.repositories.auth import create_user
from app.repositories.calculation_snapshots import create_calculation_snapshot
from app.repositories.goals import create_goal
from app.services.ai_explanation_contract import AI_EXPLANATION_SCHEMA_VERSION
from app.services.ai_explanations import (
    AiExplanationSource,
    NoSnapshotForExplanation,
    generate_or_reuse_latest_explanation,
)
from app.services.ai_provider import AiProviderError, FakeAiProvider
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session


@pytest.fixture
def engine() -> Engine:
    sqlite_engine = make_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(sqlite_engine)
    return sqlite_engine


@pytest.fixture
def db_session(engine: Engine) -> Session:
    session_factory = make_session_factory(engine)
    with session_factory() as session:
        yield session


def test_disabled_ai_returns_deterministic_fallback_without_provider_call(
    db_session: Session,
) -> None:
    user, _snapshot = _create_snapshot(db_session)
    provider = FakeAiProvider(response=_valid_response())

    result = generate_or_reuse_latest_explanation(
        db_session,
        user_id=user.id,
        provider=provider,
        settings=Settings(_env_file=None),
    )

    assert result.source is AiExplanationSource.FALLBACK
    assert result.explanation is None
    assert result.response.schema_version == AI_EXPLANATION_SCHEMA_VERSION
    assert result.response.headline == "Your plan is on track"
    assert provider.calls == []
    assert db_session.scalars(select(AIExplanation)).all() == []


def test_enabled_ai_persists_validated_response_and_sends_only_allowlisted_payload(
    db_session: Session,
) -> None:
    user, snapshot = _create_snapshot(db_session)
    provider = FakeAiProvider(response=_valid_response())
    settings = Settings(
        ai_summary_enabled=True,
        groq_api_key="test-key",
        _env_file=None,
    )

    result = generate_or_reuse_latest_explanation(
        db_session,
        user_id=user.id,
        provider=provider,
        settings=settings,
        generated_at=_timestamp(),
    )

    assert result.source is AiExplanationSource.GENERATED
    assert result.explanation is not None
    assert result.explanation.snapshot_id == snapshot.id
    assert result.explanation.response_json == _valid_response()
    assert provider.calls[0].payload == {
        "pace_status": "On Track",
        "weekly_safe_to_spend_cents": 81800,
        "projected_shortfall_cents": 0,
        "progress_percentage": 28.0,
        "remaining_weeks": 16,
        "formula_version": "pace-v1",
    }
    assert provider.calls[0].timeout_seconds == 4.0


def test_repeated_request_reuses_matching_persisted_explanation(
    db_session: Session,
) -> None:
    user, _snapshot = _create_snapshot(db_session)
    provider = FakeAiProvider(response=_valid_response())
    settings = _enabled_settings()

    first = generate_or_reuse_latest_explanation(
        db_session,
        user_id=user.id,
        provider=provider,
        settings=settings,
        generated_at=_timestamp(),
    )
    second = generate_or_reuse_latest_explanation(
        db_session,
        user_id=user.id,
        provider=provider,
        settings=settings,
        generated_at=_timestamp() + timedelta(minutes=1),
    )

    assert first.explanation is not None
    assert second.explanation is first.explanation
    assert len(provider.calls) == 1


def test_new_latest_snapshot_does_not_reuse_older_explanation(
    db_session: Session,
) -> None:
    user, first_snapshot = _create_snapshot(db_session)
    provider = FakeAiProvider(response=_valid_response())
    settings = _enabled_settings()

    first = generate_or_reuse_latest_explanation(
        db_session,
        user_id=user.id,
        provider=provider,
        settings=settings,
        generated_at=_timestamp(),
    )
    second_snapshot = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=first_snapshot.goal_id,
        formula_version="pace-v1",
        trigger="goal_updated",
        normalized_input_json={"schema_version": "snapshot-input-v1"},
        result_json=_result_json(weekly_safe_to_spend_cents=90000),
        calculated_at=_timestamp() + timedelta(minutes=1),
    )
    db_session.commit()

    second = generate_or_reuse_latest_explanation(
        db_session,
        user_id=user.id,
        provider=provider,
        settings=settings,
        generated_at=_timestamp() + timedelta(minutes=2),
    )

    assert first.explanation is not None
    assert second.explanation is not None
    assert second.explanation.snapshot_id == second_snapshot.id
    assert second.explanation.snapshot_id != first.explanation.snapshot_id
    assert len(provider.calls) == 2


def test_provider_failure_returns_fallback_without_persistence(db_session: Session) -> None:
    user, _snapshot = _create_snapshot(db_session)
    provider = FakeAiProvider(error=AiProviderError("provider failed"))

    result = generate_or_reuse_latest_explanation(
        db_session,
        user_id=user.id,
        provider=provider,
        settings=_enabled_settings(),
    )

    assert result.source is AiExplanationSource.FALLBACK
    assert result.explanation is None
    assert db_session.scalars(select(AIExplanation)).all() == []


def test_unknown_user_cannot_receive_another_users_explanation(db_session: Session) -> None:
    owner, _snapshot = _create_snapshot(db_session)
    other_user = create_user(
        db_session,
        email_normalized="other@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    provider = FakeAiProvider(response=_valid_response())
    settings = _enabled_settings()

    result = generate_or_reuse_latest_explanation(
        db_session,
        user_id=owner.id,
        provider=provider,
        settings=settings,
    )
    assert result.explanation is not None
    with pytest.raises(NoSnapshotForExplanation):
        generate_or_reuse_latest_explanation(
            db_session,
            user_id=other_user.id,
            provider=provider,
            settings=settings,
        )
    assert len(provider.calls) == 1


def test_invalid_provider_response_returns_fallback(db_session: Session) -> None:
    user, _snapshot = _create_snapshot(db_session)
    provider = FakeAiProvider(
        response={
            "schema_version": AI_EXPLANATION_SCHEMA_VERSION,
            "headline": "Spend $818",
            "body": "Unsafe numeric prose.",
            "observations": [],
            "next_step": None,
        }
    )

    result = generate_or_reuse_latest_explanation(
        db_session,
        user_id=user.id,
        provider=provider,
        settings=_enabled_settings(),
    )

    assert result.source is AiExplanationSource.FALLBACK
    assert result.explanation is None
    assert db_session.scalars(select(AIExplanation)).all() == []


def _create_snapshot(db_session: Session) -> tuple[User, CalculationSnapshot]:
    user = create_user(
        db_session,
        email_normalized="owner@example.com",
        password_hash="argon2-hash",
        time_zone="America/Los_Angeles",
    )
    goal = create_goal(
        db_session,
        user_id=user.id,
        name="Emergency fund",
        target_cents=300000,
        initial_saved_cents=50000,
        current_saved_cents=75000,
        start_date=_timestamp().date(),
        target_date=_timestamp().date() + timedelta(days=120),
        status="active",
    )
    snapshot = create_calculation_snapshot(
        db_session,
        user_id=user.id,
        goal_id=goal.id,
        formula_version="pace-v1",
        trigger="goal_updated",
        normalized_input_json={"schema_version": "snapshot-input-v1"},
        result_json=_result_json(weekly_safe_to_spend_cents=81800),
        calculated_at=_timestamp(),
    )
    db_session.commit()
    return user, snapshot


def _result_json(*, weekly_safe_to_spend_cents: int) -> dict[str, object]:
    return {
        "schema_version": "snapshot-result-v1",
        "formula_version": "pace-v1",
        "outputs": {
            "pace_status": "On Track",
            "weekly_safe_to_spend_cents": weekly_safe_to_spend_cents,
            "projected_shortfall_cents": 0,
            "progress_percentage": 28.0,
            "remaining_weeks": 16,
            "current_cash_cents": 220000,
        },
        "goal": {"name": "Private goal"},
    }


def _valid_response() -> dict[str, object]:
    return {
        "schema_version": AI_EXPLANATION_SCHEMA_VERSION,
        "headline": "Your plan is on track",
        "body": "Your current plan leaves room for weekly spending while keeping the goal in view.",
        "observations": [
            {
                "kind": "pace",
                "tone": "positive",
                "metric_refs": ["pace_status", "weekly_safe_to_spend_cents"],
            }
        ],
        "next_step": "Keep your planned expenses up to date.",
    }


def _enabled_settings() -> Settings:
    return Settings(ai_summary_enabled=True, groq_api_key="test-key", _env_file=None)


def _timestamp() -> datetime:
    return datetime(2026, 8, 29, 12, 0, tzinfo=UTC)
