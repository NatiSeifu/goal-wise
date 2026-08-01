# Implementation Specs

This directory contains implementation-ready specifications for GoalWise.

ADRs explain why the architecture is shaped a certain way. Specs define exactly how selected behavior, data contracts, and verification rules must work.

## Numbering

Specs are serially numbered for stable references:

```text
0001-pace-engine-behavior.md
0002-snapshot-json-schema.md
0003-auth-session-security.md
```

Rules:

- Spec numbers never change once created.
- Specs may be updated in place when they still describe the same contract.
- If a spec is replaced by a materially different contract, create a new spec and mark the old one `Superseded`.
- Specs should reference related ADRs.
- ADRs should reference specs only when the spec is required to understand the decision's implementation boundary.

## Status Values

Use one of these statuses:

- `Draft`: under discussion or not yet implementation-ready.
- `Accepted`: approved as the current implementation contract.
- `Superseded`: replaced by a newer spec.

## Recommended Header

```markdown
# SPEC-0001: Pace Engine Behavior

Status: Draft
Last Updated: 2026-07-31
Related ADRs: ADR-0002, ADR-0003, ADR-0004
```

## Initial Spec Candidates

These are likely worth adding before implementation:

| Spec | Purpose |
| --- | --- |
| SPEC-0001: Pace Engine Behavior | Exact formulas, pace-status decision tree, rounding, and golden scenarios |
| SPEC-0002: Snapshot JSON Schema | Stable normalized input and result JSON shapes |
| SPEC-0003: Auth and Session Security | Password hashing, session storage, cookies, CSRF, and logout behavior |
| SPEC-0004: API Response Conventions | Success envelopes, validation errors, auth errors, and ownership failures |
| SPEC-0005: Date and Time Semantics | UTC timestamps, user-local dates, recurrence expansion, and weekly plan boundaries |
| SPEC-0006: SRS Traceability | Mapping from SRS requirements to ADRs, specs, endpoints, models, and tests |

