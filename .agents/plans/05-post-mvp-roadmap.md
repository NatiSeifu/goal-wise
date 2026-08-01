# 05 - Post-MVP Roadmap

## Objective

Preserve the broader SRS requirements without forcing them into the first build. This roadmap should become the source for follow-up implementation plans after the lightweight MVP is usable.

## CSV Transactions

- Implement CSV upload with required headers `date`, `description`, and `amount`.
- Enforce UTF-8, 5 MB file limit, 10,000 row limit, and row-level validation.
- Add deterministic categories: Income, Essential Spending, Discretionary Spending, Transfer, Ignored.
- Add duplicate fingerprinting by user, date, amount, and normalized description.
- Add correction UI that preserves original imported values.
- Add tests for malformed files, partial invalid rows, duplicates, and balance-as-of exclusion.

## AI Summaries

- Add an AI provider adapter called only from the backend.
- Send only minimized aggregate payloads derived from deterministic snapshots.
- Validate AI output against a JSON schema.
- Reject summaries with unapproved numbers or prohibited advice.
- Provide deterministic fallback summaries on timeout, invalid JSON, policy failure, or disabled AI.
- Add an evaluation set for numerical consistency and safety.

## Data Rights

- Add machine-readable export for user profile, goal, financial inputs, transactions, weekly plans, and snapshots.
- Add account deletion requiring password confirmation.
- Revoke active sessions on deletion.
- Delete primary user-owned records and document backup expiration policy.
- Add tests for export ownership and post-deletion access.

## Weekly Automation

- Replace lazy weekly plan creation with a scheduled Monday 00:00 local-time process if deployment environment supports it.
- Ensure midweek recalculation never rewrites the current week's opening allowance.
- Add monitoring and retry behavior for missed scheduled jobs.

## Recommendations

- Rework `FR-PACE-011`, `FR-UI-006`, and `FR-UI-007` into deterministic, bounded recommendation rules before implementation.
- Keep recommendations category-based and avoid financial advice, borrowing advice, investment advice, tax advice, legal advice, or guaranteed outcomes.
- Prefer transparent suggestions tied to user-entered discretionary categories and projected shortfall.

## Production Hardening

- Extend login rate limiting with production monitoring, alerting, and tuning.
- Add dependency vulnerability scanning.
- Add secret scanning.
- Add structured redaction tests for logs.
- Add load tests for calculation and dashboard targets.
- Complete WCAG 2.2 AA review for primary workflows.
- Add uptime monitoring for course demo deployment.

## Roadmap Order

1. CSV transactions and correction flow.
2. Account export and deletion.
3. Weekly automation.
4. Production security hardening.
5. AI summaries and AI evaluation.
6. Advanced recommendations.
