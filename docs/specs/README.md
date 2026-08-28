# Implementation Specs

This directory contains implementation-ready specifications for GoalWise.

ADRs explain why the architecture is shaped a certain way. Specs define exactly how selected behavior, data contracts, and verification rules must work.

## Numbering

Specs are serially numbered for stable references:

```text
0001-auth-session-security.md
0002-api-response-conventions.md
0003-pace-engine-behavior.md
0004-snapshot-json-schema.md
0005-date-time-semantics.md
0006-railway-deployment.md
0007-srs-traceability-and-mvp-scope.md
0008-project-structure.md
0009-ui-mockup-and-screenshot-workflow.md
0010-planning-csv-import.md
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
# SPEC-0001: Auth and Session Security

Status: Draft
Last Updated: 2026-08-01
Related ADRs: ADR-0005, ADR-0008
```

## Index

| Spec | Title | Status |
| --- | --- | --- |
| [0001](0001-auth-session-security.md) | Auth and Session Security | Accepted |
| [0002](0002-api-response-conventions.md) | API Response Conventions | Accepted |
| [0003](0003-pace-engine-behavior.md) | Pace Engine Behavior | Accepted |
| [0004](0004-snapshot-json-schema.md) | Snapshot JSON Schema | Accepted |
| [0005](0005-date-time-semantics.md) | Date and Time Semantics | Accepted |
| [0006](0006-railway-deployment.md) | Railway Deployment | Accepted |
| [0007](0007-srs-traceability-and-mvp-scope.md) | SRS Traceability and MVP Scope | Accepted |
| [0008](0008-project-structure.md) | Project Structure | Accepted |
| [0009](0009-ui-mockup-and-screenshot-workflow.md) | UI Mockup and Screenshot Workflow | Accepted |
| [0010](0010-planning-csv-import.md) | Canonical Planning CSV Import | Draft |

## Initial Spec Candidates

Future transaction-history import and correction behavior will require a
separate specification. It is not part of SPEC-0010.
