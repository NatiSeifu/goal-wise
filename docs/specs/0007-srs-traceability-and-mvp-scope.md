# SPEC-0007: SRS Traceability and MVP Scope

Status: Accepted
Last Updated: 2026-08-21
Related ADRs: ADR-0001, ADR-0002, ADR-0003, ADR-0005, ADR-0007, ADR-0008, ADR-0009, ADR-0010, ADR-0011
Related Specs: SPEC-0001, SPEC-0002, SPEC-0003, SPEC-0004, SPEC-0005, SPEC-0006, SPEC-0010
Source: docs/srs/goal-wise-srs-v2.md

## Purpose

Define how the current architecture package maps to the broader GoalWise SRS.

This architecture represents a progressive course MVP/CDR subset, not the complete SRS v2.0 implementation. SRS v2.0 is the normative product baseline. This mapping describes the currently implemented increment and must be updated as remaining SRS v2.0 Must requirements are implemented or explicitly accepted as exceptions. SPEC-0010 and ADR-0010/0011 document the implemented canonical planning CSV increment; they do not enable raw transaction or bank-statement import.

SRS v2.0 supersedes v1.0 and narrows the MVP away from CSV import and runtime AI while adding or sharpening requirements for current-week spending, export/delete, audit events, AI Future guardrails, error contracts, observability, coverage, security evidence, and release evidence.

## Scope Status Values

| Status | Meaning |
| --- | --- |
| Implement Now | Included in the current MVP increment. |
| Partial | Implemented in a bounded MVP form that does not fully satisfy the SRS wording. |
| Deferred | Preserved for a later increment. Not implemented in the current MVP. |
| Design Constraint | Applied as a constraint even if the related feature is not implemented now. |

## Current MVP Goal

The current MVP proves the core planning loop:

1. User registers and signs in.
2. User creates one savings goal.
3. User enters manual financial assumptions.
4. Backend calculates deterministic pace results.
5. Backend stores immutable snapshots.
6. Dashboard displays safe-to-spend, pace status, progress, and calculation details.

## Implemented Planning CSV Increment

The implemented increment is the canonical planning CSV importer,
defined by [SPEC-0010](0010-planning-csv-import.md) and justified by
[ADR-0010](../adr/0010-canonical-planning-csv-import.md) and
[ADR-0011](../adr/0011-atomic-complete-plan-import.md).

Its behavior is a previewed, explicitly confirmed, atomic replacement
of one complete planning setup. This approval does not enable raw transaction
import, bank-statement parsing, transaction correction, or runtime AI. Those
remain separate deferred decisions.

## Functional Requirement Mapping

| Requirement | Scope Status | Notes |
| --- | --- | --- |
| FR-AUTH-001 | Implement Now | Registration with Argon2id password hashing. |
| FR-AUTH-002 | Implement Now | Login creates DB-backed session and CSRF token. |
| FR-AUTH-003 | Partial | Protect current MVP private data. Transaction/export/account-settings endpoints are deferred. |
| FR-AUTH-004 | Implement Now | Logout revokes current session. |
| FR-AUTH-005 | Implement Now | Cross-user private resource access returns `404` with no financial content. |
| FR-INP-008 | Accepted Exception | SRS v2.0 defines a manual-only MVP boundary; this progressive increment additionally exposes the accepted canonical planning CSV importer. Raw transaction and bank-statement import remain deferred. |
| FR-GOAL-001 | Implement Now | One active goal. |
| FR-GOAL-002 | Implement Now | Validate money and dates using user local date. |
| FR-GOAL-003 | Implement Now | Prevent second active goal; support complete/archive lifecycle. |
| FR-GOAL-004 | Implement Now | Valid goal edits create snapshots when required inputs are complete. |
| FR-GOAL-005 | Implement Now | Completed lifecycle and zero goal gap behavior. |
| FR-FIN-001 | Implement Now | Manual financial profile. |
| FR-FIN-002 | Implement Now | Manual income sources. |
| FR-FIN-003 | Implement Now | Unconfirmed income excluded from forecast resources. |
| FR-FIN-004 | Implement Now | Manual planned expenses. |
| FR-FIN-005 | Implement Now | Date-only occurrence semantics in SPEC-0005. |
| FR-FIN-006 | Implement Now | 5% rounded-up reserve buffer suggestion; `$0` allowed when confirmed income is zero. |
| FR-FIN-007 | Implement Now | Valid financial changes create snapshots when required inputs are complete. |
| FR-TXN-001 through FR-TXN-008 | Deferred | Raw transaction/bank-statement import, transaction correction, duplicate handling, and transaction calculations are later increments. Canonical planning CSV import is implemented separately by SPEC-0010. |
| FR-PACE-001 | Implement Now | Required outputs defined in SPEC-0003. |
| FR-PACE-002 | Implement Now | Integer cents and whole-dollar downward rounding. |
| FR-PACE-003 | Implement Now | Remaining weeks minimum is one. |
| FR-PACE-004 | Implement Now | Off Pace shortfall behavior. |
| FR-PACE-005 | Implement Now | Snapshot comparison supports changed input categories and safe-to-spend delta. |
| FR-PACE-006 | Implement Now | Immutable calculation snapshots. |
| FR-PACE-007 | Partial | MVP lazily creates current weekly plan on authenticated dashboard access instead of running a Monday background scheduler. |
| FR-PACE-008 | Partial | Current-week remainder is backend-computed; transaction-based discretionary outflows are deferred until transaction support exists. |
| FR-PACE-009 | Implement Now | Midweek recalculation does not replace current week opening allowance. |
| FR-PACE-010 | Implement Now | Pace status decision tree in SPEC-0003. |
| FR-PACE-011 | Deferred | Recommendation behavior must be rewritten as bounded deterministic rules before implementation. |
| FR-UI-001 | Partial | Dashboard shows MVP fields; transaction-based current-week spending waits for transaction support. |
| FR-UI-002 | Implement Now | Calculation details from latest snapshot. |
| FR-UI-003 | Implement Now | Missing-input state blocks misleading safe-to-spend output. |
| FR-UI-004 | Implement Now | Save valid inputs and refresh dashboard without full page reload. |
| FR-UI-005 | Deferred | Progress chart is later UI enhancement. Backend can still provide progress percentage now. |
| FR-UI-006 | Deferred | Overspending recommendation depends on transaction/current-week spending support. |
| FR-UI-007 | Deferred | Month-end spending suggestions are later deterministic recommendation work. |
| FR-UI-008 | Implement Now | Field validation and canonical planning CSV row errors are included now. |
| FR-AI-001 through FR-AI-007 | Deferred | AI summaries are not in the current MVP runtime. Deterministic core must remain AI-free. |
| FR-DATA-001 | Deferred | Export is later data-rights work and should come after this MVP subset is complete. |
| FR-DATA-002 | Deferred | Account deletion is later data-rights work and should come after this MVP subset is complete. |
| FR-DATA-003 | Design Constraint | MVP must not request or store bank credentials, card PINs, full card numbers, brokerage credentials, or similar sensitive credentials. |

## Non-Functional Requirement Mapping

| Requirement | Scope Status | Notes |
| --- | --- | --- |
| NFR-ACC-001 | Implement Now | Golden tests for pace engine. |
| NFR-ACC-002 | Implement Now | Determinism tests use identical normalized inputs, timestamps, time zone, and formula version. |
| NFR-PERF-001 | Deferred | Full load target with 10,000 transactions waits for transaction support and production hardening. |
| NFR-PERF-002 | Implement Now | Dashboard responsiveness should be smoke-tested for MVP demo. |
| NFR-PERF-003 | Deferred | AI latency applies only when AI summaries are enabled. |
| NFR-SEC-001 | Implement Now | Argon2id password hashing. |
| NFR-SEC-002 | Implement Now | Railway-hosted traffic uses HTTPS. |
| NFR-SEC-003 | Implement Now | Login rate limiting: 5 failed attempts within 10 minutes by account and source. |
| NFR-SEC-004 | Partial | Session expiry and logout revocation now; password-change endpoint is deferred. If added later, password change must revoke active sessions. |
| NFR-SEC-005 | Implement Now | Server-side ownership checks for current MVP protected endpoints. |
| NFR-SEC-006 | Implement Now | ORM/parameterized access and server-side validation. |
| NFR-SEC-007 | Implement Now | Railway service variables; no committed secrets. |
| NFR-SEC-008 | Partial | Canonical planning CSV uploads are bounded by file-size and row-count limits; upload rate limiting remains later hardening. |
| NFR-SEC-009 | Deferred | Full dependency vulnerability gate is production hardening; basic dependency care still expected. |
| NFR-PRI-001 | Implement Now | Data minimization; no bank/payment credentials. |
| NFR-PRI-002 | Implement Now | Logs exclude sensitive values. |
| NFR-PRI-003 | Deferred | AI payload minimization applies when AI summaries are enabled. |
| NFR-PRI-004 | Deferred | Account deletion and backup expiration are later data-rights work after this MVP subset is complete. |
| NFR-REL-001 | Implement Now | Confirmed planning CSV replacement is atomic and rolls back on persistence failure. |
| NFR-REL-002 | Partial | Course demo availability is supported by Railway deployment and health check; full monitoring is post-MVP. |
| NFR-REL-003 | Implement Now | AI provider loss cannot affect MVP because runtime AI is absent. |
| NFR-USA-001 | Implement Now | Primary workflow should be demoable in under five minutes. |
| NFR-USA-002 | Implement Now | Dashboard explanation should support comprehension. |
| NFR-A11Y-001 | Partial | MVP requires smoke accessibility checks; full WCAG audit evidence is later hardening. |
| NFR-A11Y-002 | Implement Now | Keyboard and focus behavior for primary workflow. |
| NFR-MNT-001 | Implement Now | Maintainable repo structure and CI-ready tests. |
| NFR-MNT-002 | Implement Now | Pace-engine coverage target should guide implementation. |
| NFR-MNT-003 | Implement Now | Formula changes require version and golden tests. |
| NFR-AIQ-001 through NFR-AIQ-003 | Deferred | AI quality requirements apply when AI summaries are enabled. |

## Verification

Required review checks:

- Every SRS requirement has a scope status.
- Deferred requirements are not exposed as working MVP features in navigation or demos.
- Partial requirements name the MVP limitation clearly.
- Implement Now requirements are represented in ADRs, specs, plans, endpoints, models, or tests.
- Future increments preserve the deterministic core and normalized-input boundaries.
