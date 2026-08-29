# Phase 13 - Bounded AI Explanation Layer

## Objective

Add an optional, post-MVP AI explanation feature that makes a committed
calculation snapshot easier to understand without moving any financial
authority out of the deterministic backend path.

The source of truth is [SPEC-0011](../../docs/specs/0011-ai-explanation-layer.md)
and [ADR-0012](../../docs/adr/0012-bounded-ai-explanation-layer.md).

## Scope boundary

Included:

- server-configured feature enablement and trigger mode;
- explicit request mode by default;
- synchronous provider call with a four-second timeout;
- provider adapter and fake provider for tests;
- Groq API as the first provider implementation, using
  `llama-3.3-70b-versatile` by default;
- allowlisted snapshot payload;
- versioned structured response validation;
- snapshot-scoped persistence and reuse;
- explicit retryable unavailable state when AI cannot produce accepted output;
- user-facing generated summary presentation.

Deferred:

- transaction classification;
- automatic trigger as the default;
- autonomous agents, RAG, fine-tuning, or multi-step orchestration;
- financial recommendations or calculations;
- provider selection by users;
- export/delete changes until those workflows are implemented.

## Phase 1 - Contract and configuration

### Slice 1 - Accept the AI contract

Create or update the spec, ADR index, and implementation index. Confirm the
allowlisted payload, response schema, snapshot lifecycle, persistence policy,
failure behavior, and prohibition on authoritative AI output.

Success criteria:

- SPEC-0011 and ADR-0012 are internally consistent with the SRS and ADR-0002.
- The implementation plan names testable slices and no deferred behavior is
  presented as current MVP functionality.

### Slice 2 - Server-side configuration

Add typed settings for enablement, trigger mode, provider configuration, model,
prompt version, response schema version, and the four-second timeout. Configure
Groq through `GROQ_API_KEY`, keep the feature disabled by default, and keep all
secrets out of frontend configuration.

Success criteria:

- Missing AI configuration leaves the application bootable.
- Invalid trigger or timeout configuration fails clearly at startup or uses a
  documented safe default.
- Frontend bundles contain no provider credentials.
- Groq and `llama-3.3-70b-versatile` are the default provider/model values.
- Unit tests prove disabled configuration makes zero provider calls.

## Phase 2 - Provider boundary and validation

### Slice 3 - Provider adapter protocol

Define an application-level provider protocol and one implementation boundary.
Add a deterministic fake provider for tests; do not couple routes or domain
services to a vendor SDK.

Success criteria:

- The adapter accepts the minimized payload and returns raw structured data.
- Provider errors and timeout behavior are represented without leaking vendor
  details through the API.
- Tests can run without network access or an API key.

### Slice 4 - Payload and response validators

Implement allowlisted payload construction and strict response validation for
`ai-explanation-v1`. Reject unknown fields, unsupported metric references,
unsafe text, excessive lengths, and malformed responses.

Success criteria:

- Payload tests prove prohibited fields never leave the application.
- Valid responses pass normalization.
- Invalid, unsafe, and inconsistent responses produce typed failures.
- Numeric display values are always sourced from the snapshot, not generated
  prose.

## Phase 3 - Snapshot explanation service

### Slice 5 - Explanation persistence model

Add an `AIExplanation` persistence model and migration linked to a calculation
snapshot and owner. Store validated response JSON plus provider/model, prompt,
schema, and generation metadata. Add a uniqueness rule for the reusable
version tuple.

Success criteria:

- An explanation cannot be attached to another user or an unknown snapshot.
- Prior explanations remain unchanged when a new snapshot is created.
- The model is compatible with SQLite tests and PostgreSQL deployment.

### Slice 6 - Generate-or-reuse service

Implement the service that loads the latest requested user-owned snapshot,
returns a matching stored explanation when available, otherwise builds the
allowlisted payload, calls the adapter, validates the response, persists it,
and returns the result. Raise a typed unavailable error for expected AI
failures; do not manufacture an explanation when the provider does not produce
accepted output.

Success criteria:

- Generation never calls the pace engine or mutates financial data.
- A new snapshot does not reuse an older snapshot explanation.
- Repeated requests for the same version tuple reuse the stored result.
- Provider timeout is four seconds and core workflows remain available.

## Phase 4 - API and frontend workflow

### Slice 7 - Authenticated explanation endpoint

Add a versioned authenticated endpoint for an explicit explanation request.
Apply existing CSRF and ownership rules where the method is unsafe. Return
source snapshot metadata and user-facing generated content without exposing
provider internals; return a generic retryable error when generation fails.

Success criteria:

- Missing, cross-user, and unknown snapshots follow existing private-resource
  response conventions.
- Disabled, failed, and successful requests have stable response envelopes.
- API tests cover ownership, CSRF, unavailable errors, and reuse behavior.

### Slice 8 - Generated summary presentation

Add an explicit action on the dashboard or calculation-details surface. Show
loading, success, and retryable error states without blocking official values.
Render accepted structured content as natural text and trusted metric values.
Clearly label generated content with snapshot timestamp and formula version.

Success criteria:

- The latest snapshot never displays a stale explanation as current.
- The feature is invisible or clearly guarded when disabled.
- Core dashboard values remain usable during provider delay or failure.
- The UI renders generated text safely and accessibly.

## Phase 5 - Safety evaluation and rollout

### Slice 9 - Automated safety and regression suite

Add contract, privacy, timeout, prohibited-advice, numeric-consistency,
failure-handling, persistence, and frontend workflow tests. Use a fake provider in CI;
no live provider call belongs in the normal test suite.

Success criteria:

- All SRS FR-AI-002 through FR-AI-007 checks have traceable tests or inspection
  evidence.
- Provider payloads are inspected for prohibited data.
- The application passes with AI disabled and with the fake provider enabled.

### Slice 10 - Human evaluation and controlled enablement

Create a small reviewed evaluation set covering every supported pace status,
positive and zero allowance, projected shortfall, and changed snapshots.
Record human judgments for accuracy, readability, prohibited advice, and
numeric consistency before enabling a real provider in a non-production
environment.

Success criteria:

- The team approves objective pass/fail criteria before live enablement.
- Staging can enable the feature without changing frontend code.
- Automatic mode remains off unless separately approved and evaluated.

## Suggested commit slices

1. `docs: specify bounded AI explanations`
2. `chore: configure AI summary settings`
3. `feat: add AI provider boundary`
4. `feat: validate AI explanation contracts`
5. `feat: persist snapshot explanations`
6. `feat: generate or reuse snapshot explanations`
7. `feat: expose explanation endpoint`
8. `feat: add generated summary UI`
9. `test: cover AI explanation safety and failure handling`
10. `docs: record AI evaluation results`

## Phase completion criteria

Phase 13 is complete when:

- AI is disabled by default and can be enabled only through server configuration;
- explicit request mode is the default;
- the provider receives only the approved minimized payload;
- valid responses are persisted per exact snapshot and version tuple;
- new snapshots never show stale explanations as current;
- four-second timeout and all expected provider failures return a generic
  retryable error;
- no AI output changes official financial values;
- frontend and backend tests cover privacy, safety, ownership, and usability;
- human evaluation evidence supports any staging enablement.
