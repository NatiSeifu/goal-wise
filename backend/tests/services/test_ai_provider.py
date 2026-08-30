import json
from unittest.mock import patch

import pytest
from app.services.ai_prompts import (
    AI_EXPLANATION_PROMPT_V3,
    AI_EXPLANATION_PROMPT_VERSION,
)
from app.services.ai_provider import (
    AiProviderError,
    AiProviderTimeout,
    FakeAiProvider,
    GroqAiProvider,
    ProviderCall,
)
from pydantic import SecretStr


def test_active_prompt_version_explains_status_and_spending_together() -> None:
    assert AI_EXPLANATION_PROMPT_VERSION == "ai-explanation-prompt-v3"
    assert '"At Risk"' in AI_EXPLANATION_PROMPT_V3
    assert "projected shortfall is zero" in AI_EXPLANATION_PROMPT_V3
    assert "cut spending" in AI_EXPLANATION_PROMPT_V3
    assert "Never contradict a supplied metric" in AI_EXPLANATION_PROMPT_V3


class StubHttpResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> "StubHttpResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body


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


def test_groq_provider_sends_minimal_json_request_and_decodes_json_content() -> None:
    provider_response = {
        "choices": [
            {"message": {"content": '{"schema_version":"ai-explanation-v1","headline":"Good"}'}}
        ]
    }
    provider = GroqAiProvider(
        api_key=SecretStr("groq-test-key"),
        model="openai/gpt-oss-120b",
        system_prompt="Return the approved schema.",
    )

    with patch(
        "app.services.ai_provider.request.urlopen",
        return_value=StubHttpResponse(json.dumps(provider_response).encode()),
    ) as urlopen:
        result = provider.generate(
            payload={"pace_status": "On Track"},
            timeout_seconds=4.0,
        )

    request = urlopen.call_args.args[0]
    request_body = json.loads(request.data)
    assert result == {"schema_version": "ai-explanation-v1", "headline": "Good"}
    assert request.full_url == "https://api.groq.com/openai/v1/chat/completions"
    assert request.headers["Authorization"] == "Bearer groq-test-key"
    assert request.headers["User-agent"] == "GoalWise/1.0"
    assert request_body["model"] == "openai/gpt-oss-120b"
    assert request_body["response_format"] == {"type": "json_object"}
    assert request_body["temperature"] == 0
    assert request_body["messages"] == [
        {"role": "system", "content": "Return the approved schema."},
        {"role": "user", "content": '{"pace_status": "On Track"}'},
    ]
    assert urlopen.call_args.kwargs["timeout"] == 4.0


def test_groq_provider_maps_timeout_to_provider_timeout() -> None:
    provider = GroqAiProvider(api_key=SecretStr("groq-test-key"), model="test-model")

    with (
        patch(
            "app.services.ai_provider.request.urlopen",
            side_effect=TimeoutError,
        ),
        pytest.raises(AiProviderTimeout, match="timed out"),
    ):
        provider.generate(payload={}, timeout_seconds=4.0)


def test_groq_provider_rejects_invalid_response_envelope() -> None:
    provider = GroqAiProvider(api_key=SecretStr("groq-test-key"), model="test-model")

    with (
        patch(
            "app.services.ai_provider.request.urlopen",
            return_value=StubHttpResponse(b'{"choices":[]}'),
        ),
        pytest.raises(AiProviderError, match="response"),
    ):
        provider.generate(payload={}, timeout_seconds=4.0)
