"""Provider boundary for optional AI explanation generation."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol

AiPayload = Mapping[str, object]
AiResponse = Mapping[str, object]


class AiProviderError(RuntimeError):
    """Base error for expected provider failures."""


class AiProvider(Protocol):
    """Application-facing contract implemented by AI providers."""

    def generate(
        self,
        *,
        payload: AiPayload,
        timeout_seconds: float,
    ) -> AiResponse:
        """Generate a raw structured response for an approved payload."""


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
