import pytest
from app.services.ai_provider import (
    AiProviderError,
    FakeAiProvider,
    ProviderCall,
)


def test_fake_provider_returns_configured_response_and_records_call() -> None:
    response = {"schema_version": "ai-explanation-v1", "headline": "Good progress"}
    payload = {"pace_status": "On Track", "weekly_safe_to_spend_cents": 81800}
    provider = FakeAiProvider(response=response)

    result = provider.generate(payload=payload, timeout_seconds=4.0)

    assert result == response
    assert provider.calls == [ProviderCall(payload=payload, timeout_seconds=4.0)]


def test_fake_provider_can_raise_a_configured_provider_error() -> None:
    provider = FakeAiProvider(error=AiProviderError("provider unavailable"))

    with pytest.raises(AiProviderError, match="provider unavailable"):
        provider.generate(payload={}, timeout_seconds=4.0)

    assert provider.calls == [ProviderCall(payload={}, timeout_seconds=4.0)]
