# SPEC-0011: Bounded AI Explanation Layer

Status: Accepted
Last Updated: 2026-08-29
Related ADRs: ADR-0002, ADR-0003, ADR-0007, ADR-0012
Related Specs: SPEC-0002, SPEC-0003, SPEC-0004, SPEC-0007
Source Requirements: FR-AI-001 through FR-AI-007, NFR-PRI-003, NFR-REL-003, NFR-AIQ-001 through NFR-AIQ-003

## Purpose

Define a post-MVP, optional AI layer that explains a committed GoalWise
calculation snapshot in natural language. The feature is an explanation
surface, not a calculation, recommendation, transaction-classification, or
planning-authority feature.

The current MVP may continue to run with the feature disabled and no provider
configured. The deterministic dashboard remains the authoritative source of
financial values; it is not presented as an AI explanation.

## Scope

Included:

- one explanation for one committed calculation snapshot;
- explicit user-request mode as the default;
- server-side configuration for whether the feature is enabled and how it is triggered;
- synchronous provider invocation with a four-second timeout;
- provider-independent adapter boundary;
- minimized aggregate payload;
- strict response validation with an explicit unavailable state on failure;
- persistence scoped to the exact snapshot, model, prompt, and response schema versions;
- natural user-facing rendering of accepted structured content.

The initial provider is the Groq API using `openai/gpt-oss-120b` as the
default model. This is an implementation choice behind the provider adapter,
not part of the application-level explanation response contract.

Deferred:

- AI calculation, recommendations, or overrides;
- transaction classification;
- raw transaction or bank-statement input;
- autonomous agents, retrieval, fine-tuning, or multi-step orchestration;
- automatic generation as the default;
- user-configurable provider or trigger settings;
- export and deletion behavior for generated explanations until those workflows are implemented.

## Configuration

Configuration is server-side only. The frontend must not choose a provider,
model, API key, or trigger mode.

Required configuration concepts:

- `AI_SUMMARY_ENABLED`: disabled by default; when disabled, zero provider calls
  are permitted;
- `AI_SUMMARY_TRIGGER`: `request` or `automatic`, defaulting to `request`;
- `GROQ_API_KEY`: provider credential read only by the backend runtime secret
  store;
- `AI_SUMMARY_PROVIDER`: defaults to `groq` for the first implementation;
- `AI_SUMMARY_MODEL`: defaults to `openai/gpt-oss-120b`;
- provider timeout fixed at four seconds for this increment;
- prompt version and response schema version controlled by the application.

The active prompt is `ai-explanation-prompt-v3`. It requires the explanation to
interpret pace status, weekly spending room, and projected shortfall together.
For example, an `At Risk` pace with positive weekly spending room and no
projected shortfall must be described as a goal-pace concern, not as an
immediate inability to spend. The generated next step must be proportionate to
the supplied metrics and must not recommend cutting spending unless the data
supports that warning. User-facing copy must avoid technical phrases such as
"risk signal" and "savings pace assumptions."

Automatic mode is a configuration extension, not a reason to add calls to
ordinary dashboard reads or input-save requests unless explicitly enabled.

## Snapshot lifecycle

1. A goal or financial-input change uses the existing deterministic service
   path and creates a new immutable snapshot when the change is committed.
2. Existing explanations remain attached to the snapshots they describe.
3. The latest snapshot has no current AI explanation until one is generated for
   that snapshot.
4. The dashboard must not display an explanation from an older snapshot as if
   it describes the latest result.
5. In default request mode, the UI presents an explicit action to generate an
   explanation for the latest snapshot.
6. Repeating a request for the same snapshot and version tuple may reuse the
   stored validated explanation rather than calling the provider again.

## Approved provider input

The provider payload may contain only these snapshot-derived values:

- `pace_status`;
- `weekly_safe_to_spend_cents`;
- `projected_shortfall_cents`;
- `progress_percentage`;
- `remaining_weeks`;
- `formula_version`;
- non-identifying goal context, if needed for readability.

The first implementation must not send the user-authored goal name. It must
not send email addresses, authentication or session data, snapshot IDs, raw
transaction descriptions, transaction rows, full financial profiles, raw
income or expense names, provider secrets, or unneeded timestamps.

The backend constructs this payload from the stored snapshot. The client cannot
provide or alter the provider payload.

## Provider response contract

The provider must return JSON matching the active response schema. The first
schema is intentionally small:

```json
{
  "schema_version": "ai-explanation-v1",
  "headline": "string",
  "body": "string",
  "observations": [
    {
      "kind": "pace | allowance | progress | shortfall",
      "tone": "positive | neutral | caution",
      "metric_refs": ["weekly_safe_to_spend_cents"]
    }
  ],
  "next_step": "string or null"
}
```

Rules:

- `headline`, `body`, and `next_step` are natural-language user-facing text;
- `observations` may reference only an approved metric enum;
- the provider must not emit authoritative numeric values in prose; the UI
  renders trusted values from the snapshot when a metric is referenced;
- text length, observation count, and metric-reference count are bounded;
- text containing prohibited financial-advice categories is rejected;
- malformed JSON, unknown fields, unknown enums, missing required fields,
  excessive length, or unsupported metric references are rejected;
- the stored object includes the schema version and generation metadata.

This lets the provider sound natural while trusted numbers remain rendered from
the deterministic snapshot rather than copied from generated prose.

## Persistence

An accepted explanation is associated internally with:

- the owning user;
- the exact calculation snapshot;
- provider and model identifiers;
- prompt version;
- response schema version;
- generated timestamp;
- validated response JSON.

The provider must not receive the internal snapshot ID. At most one reusable
accepted explanation should exist for a given snapshot/provider/model/prompt/
schema tuple. Failed responses are not presented as accepted explanations.

## Request and failure behavior

The authenticated explanation status response and successful explanation
response include a non-sensitive `enabled` boolean so the frontend can avoid
rendering the explanation workflow when the feature is unavailable. They do not
expose the provider, model, prompt, credential state, or provider error
details.

- Explanation requests require authentication and the existing ownership
  checks for the requested snapshot.
- The request must target a committed snapshot and must not trigger a new
  financial calculation.
- The provider call is synchronous and is cancelled or treated as failed
  after four seconds.
- Disabled configuration, missing provider configuration, timeout, provider
  error, invalid response, unsafe text, or inconsistent references return a
  generic `503 ai_explanation_unavailable` error. The UI tells the user that
  the explanation could not be prepared and offers a retry; it does not present
  deterministic prose as if it were AI-generated.
- Core dashboard, calculation, input, and goal workflows remain available
  when AI fails.
- The API must not expose provider errors, prompts, secrets, or raw payloads.
- A generated explanation is labeled as generated and includes the source
  snapshot timestamp and formula version in the user-facing view.

There is no user-facing AI fallback. The deterministic dashboard values remain
available when an explanation request fails, and the explanation panel reports
the failure without persisting an ungenerated response.

## Security and privacy

- Provider calls are server-to-server only.
- Secrets are read from runtime configuration and never sent to the frontend.
- Payload construction uses an allowlist, not a denylist.
- User ownership is checked before reading a snapshot or explanation.
- Generated text is untrusted input and must be safely rendered as text, not
  interpreted as HTML or executable markup.
- Logs must contain outcome metadata only; do not log prompts, responses,
  financial values, raw descriptions, tokens, or credentials.

## Verification requirements

Tests must prove:

- disabled configuration makes zero provider calls;
- default trigger mode is explicit request;
- only the approved aggregate fields enter the provider payload;
- another user's snapshot cannot be explained;
- a new snapshot does not reuse an older snapshot's explanation as current;
- valid structured output is persisted and reused for the same version tuple;
- malformed, overlong, unsafe, or inconsistent responses return the generic
  unavailable error;
- provider errors and four-second timeouts return the generic unavailable error
  without breaking core APIs;
- generated content is labeled and source metadata is shown;
- numeric values displayed in the explanation come from the trusted snapshot;
- the feature does not calculate or modify any official financial output.
