"""Provider boundary for optional AI explanation generation."""

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol
from urllib import error, request

from pydantic import SecretStr

AiPayload = Mapping[str, object]
AiResponse = Mapping[str, object]


class AiProviderError(RuntimeError):
    """Base error for expected provider failures."""


class AiProviderTimeout(AiProviderError):
    """Raised when a provider does not respond within the configured timeout."""


class AiProvider(Protocol):
    """Application-facing contract implemented by AI providers."""

    def generate(
        self,
        *,
        payload: AiPayload,
        timeout_seconds: float,
    ) -> AiResponse:
        """Generate a raw structured response for an approved payload."""


class GroqAiProvider:
    """Groq chat-completions adapter behind the application provider contract."""

    endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(
        self,
        *,
        api_key: SecretStr,
        model: str,
        system_prompt: str = "Return a valid JSON object matching the requested schema.",
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._system_prompt = system_prompt

    def generate(
        self,
        *,
        payload: AiPayload,
        timeout_seconds: float,
    ) -> AiResponse:
        request_body = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": self._system_prompt},
                {"role": "user", "content": json.dumps(dict(payload))},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        outbound_request = request.Request(
            self.endpoint,
            data=json.dumps(request_body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key.get_secret_value()}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(outbound_request, timeout=timeout_seconds) as response:
                response_body = response.read()
        except TimeoutError as exc:
            raise AiProviderTimeout("AI provider request timed out.") from exc
        except error.HTTPError as exc:
            raise AiProviderError("AI provider request failed.") from exc
        except error.URLError as exc:
            raise AiProviderError("AI provider request failed.") from exc

        try:
            envelope = json.loads(response_body)
            content = envelope["choices"][0]["message"]["content"]
            decoded_response = json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise AiProviderError("AI provider returned an invalid response.") from exc

        if not isinstance(decoded_response, Mapping):
            raise AiProviderError("AI provider returned an invalid response.")
        return dict(decoded_response)


@dataclass(frozen=True, slots=True)
class ProviderCall:
    """A recorded provider invocation used by tests and diagnostics."""

    payload: dict[str, object]
    timeout_seconds: float


@dataclass
class FakeAiProvider:
    """Deterministic provider double for tests without network access."""

    response: AiResponse = field(default_factory=dict)
    error: AiProviderError | None = None
    calls: list[ProviderCall] = field(default_factory=list)

    def generate(
        self,
        *,
        payload: AiPayload,
        timeout_seconds: float,
    ) -> AiResponse:
        self.calls.append(ProviderCall(payload=dict(payload), timeout_seconds=timeout_seconds))
        if self.error is not None:
            raise self.error
        return self.response
