# 00 - MVP Scope Plan

## Objective

Convert the GoalWise SRS into a lightweight, buildable MVP that proves the core product loop: a user signs in, enters one savings goal and manual financial assumptions, receives a deterministic weekly safe-to-spend amount, and can inspect how it was calculated.

## MVP Includes

- Account registration, login, logout, authenticated access, and user-owned data isolation.
- One active savings goal with target amount, current saved amount, start date, target date, and time zone.
- Manual financial profile with starting cash, balance-as-of date, and reserve buffer.
- Manual income sources with confirmed or unconfirmed confidence.
- Manual planned expenses with essential or discretionary classification.
- Deterministic pace engine using integer cents and formula version `pace-v1`.
- Immutable calculation snapshots after valid goal or financial input changes.
- Dashboard with goal progress, pace status, weekly safe-to-spend, missing-input states, and calculation details.
- Focused backend, engine, API, and dashboard tests.

## Deferred From MVP

- CSV import, row-level import reports, duplicate transaction handling, and transaction correction UI.
- AI summaries, AI provider calls, JSON-schema validation for AI output, and AI evaluation datasets.
- Account export, confirmed account deletion, and backup retention workflows.
- Automatic Monday background jobs for weekly plan creation.
- Advanced recommendation lists, especially month-end spending suggestions and AI-like coaching.
- Production load tests, uptime monitoring, and full WCAG audit evidence.
- Multiple simultaneous goals, live banking, transfers, payments, credit, tax, investment, or advisory features.

## Requirement Mapping

- Implement now: `FR-AUTH-001` through `FR-AUTH-005`, `FR-GOAL-001` through `FR-GOAL-005`, `FR-FIN-001` through `FR-FIN-007`, `FR-PACE-001` through `FR-PACE-010`, `FR-UI-001` through `FR-UI-004`, `FR-UI-008`, `FR-DATA-003`.
- Partially implement now: weekly plan behavior from `FR-PACE-007` through `FR-PACE-009` using dashboard-access creation instead of a background scheduler.
- Defer: `FR-TXN-001` through `FR-TXN-008`, `FR-AI-001` through `FR-AI-007`, `FR-DATA-001`, `FR-DATA-002`, `FR-UI-005` through `FR-UI-007`.
- Keep as design constraints now: money as integer cents, formula versioning, no bank credentials, protected endpoints, deterministic calculations, no sensitive values in logs.

## Implementation Steps

1. Scaffold the application according to `DESIGN.md`.
2. Build auth and persistence foundation.
3. Build goal and financial input CRUD.
4. Build pace engine as a pure module with golden tests.
5. Wire recalculation and immutable snapshots into service methods.
6. Build dashboard read model and UI.
7. Add MVP traceability notes to README or project docs after implementation.

## Acceptance Criteria

- A new user can register, log in, create one goal, enter financial assumptions, and view a valid weekly safe-to-spend result.
- Unauthenticated users cannot access private data.
- A user cannot read or modify another user's goal or financial data by changing identifiers.
- Changing a valid goal or financial input creates a new calculation snapshot.
- The dashboard explains the current formula inputs without requiring a page reload after save.
- Pace-engine golden tests pass for on-track, off-pace, completed, ahead, at-risk, and less-than-one-week scenarios.

