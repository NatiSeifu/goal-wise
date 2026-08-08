# Phase 5 - Dashboard Snapshots Backend

## Purpose

Connect persisted goal and financial inputs to the deterministic pace engine, store immutable calculation snapshots, and expose backend dashboard data that the future React UI can render without duplicating financial formulas.

This is an execution plan, not a new implementation contract. The source of truth remains:

- `docs/specs/0002-api-response-conventions.md`
- `docs/specs/0003-pace-engine-behavior.md`
- `docs/specs/0004-snapshot-json-schema.md`
- `docs/specs/0005-date-time-semantics.md`
- `docs/specs/0007-srs-traceability-and-mvp-scope.md`
- `docs/specs/0008-project-structure.md`
- `docs/adr/0001-layered-modular-monolith.md`
- `docs/adr/0002-deterministic-pace-engine-no-runtime-ai.md`
- `docs/adr/0003-immutable-calculation-snapshots.md`
- `docs/adr/0004-money-integer-cents-and-formula-versioning.md`
- `docs/adr/0005-auth-sessions-and-ownership.md`
- `docs/adr/0006-versioned-rest-api.md`
- `.agents/plans/03-pace-engine-and-snapshots.md`
- `.agents/plans/04-dashboard-mvp.md`
- `.agents/implementation/phase-04-goals-and-financial-inputs.md`

## Scope

In scope:

- persistence model and migration for immutable calculation snapshots;
- optional MVP persistence model and migration for weekly plans if pulled into this branch;
- repository methods for inserting and reading user-owned snapshots;
- snapshot JSON normalization matching `snapshot-input-v1` and `snapshot-result-v1`;
- service behavior that prepares pace input, runs `calculate_pace`, and stores a snapshot when inputs are complete;
- comparison against the previous snapshot for changed input categories and weekly safe-to-spend delta;
- authenticated dashboard/latest-snapshot API routes;
- focused tests for immutability, schema shape, ownership, missing inputs, and API behavior.

Out of scope:

- React dashboard UI;
- CSV transaction import;
- transaction persistence;
- optional AI summaries;
- background weekly scheduler;
- export/delete-account workflows.

## Design Direction

Build the backend dashboard contract first:

```text
Persisted user inputs
  -> prepare_pace_input_for_user(...)
  -> calculate_pace(...)
  -> insert CalculationSnapshot
  -> dashboard/latest snapshot API response
```

The frontend must receive calculated values from backend APIs. React may format values, but it must not calculate official pace status, safe-to-spend, progress percentage, current-week allowance, remainder, projected shortfall, remaining weeks, or changed-input deltas.

## Decisions to Discuss Before Coding

- Trigger timing: create snapshots synchronously inside valid input-write services/routes, or expose a dedicated recalculation service endpoint first.
- Dashboard endpoint shape: one combined `/api/v1/dashboard` response, separate `/api/v1/calculation-snapshots/latest`, or both.
- Weekly plan timing: include lazy weekly-plan creation in this phase, or defer it to the first frontend dashboard phase.
- Snapshot comparison depth: start with category-level diffs only, or also identify specific income/expense IDs that changed.
- Snapshot JSON validation: enforce with Pydantic models, typed dicts plus tests, or a JSON Schema fixture.

## Slice 1 - Calculation Snapshot Model and Migration

Build:

- `backend/app/models/calculation_snapshot.py`;
- Alembic migration for `calculation_snapshots`;
- model metadata imports;
- database tests for table shape, ownership, JSON columns, and migration downgrade.

Suggested fields:

- `id`;
- `user_id`;
- `goal_id`;
- `formula_version`;
- `trigger`;
- `normalized_input_json`;
- `result_json`;
- `calculated_at`;
- `created_at`.

Success criteria:

- snapshots belong to authenticated users;
- snapshots reference the goal used for calculation;
- JSON columns work in SQLite tests and remain PostgreSQL-compatible;
- formula version and trigger are stored as strings;
- snapshots have no `updated_at` column;
- migration upgrades and downgrades in SQLite tests;
- `make backend-check` passes.

## Slice 2 - Snapshot Repository

Build:

- create snapshot;
- get latest snapshot for user;
- get latest snapshot for user and goal;
- get previous snapshot before a given snapshot or timestamp;
- optional list method with a conservative limit for future history views.

Success criteria:

- every query filters by authenticated `user_id`;
- cross-user snapshot lookup behaves like missing data;
- latest snapshot ordering is deterministic by `calculated_at` and `id`;
- repository creates snapshots by insert only;
- repository tests prove existing snapshot JSON is not mutated by later input changes;
- `make backend-check` passes.

## Slice 3 - Snapshot JSON Builder

Build:

- normalized input JSON builder for `snapshot-input-v1`;
- result JSON builder for `snapshot-result-v1`;
- progress percentage calculation;
- explanation payload with included/excluded income and expense IDs;
- changed-from-previous payload.

Success criteria:

- normalized input JSON includes `schema_version`, `formula_version`, `calculation`, `goal`, `financial_profile`, `income_sources`, `planned_expenses`, and `transactions`;
- result JSON includes `schema_version`, `formula_version`, `outputs`, `explanation`, and `changed_from_previous`;
- output fields cover all required pace-engine outputs plus `progress_percentage`, `current_week_opening_allowance_cents`, and `current_week_remainder_cents` when dashboard data uses them;
- snapshot inputs include goal, income, and expense names;
- snapshot transaction entries remain empty until transaction support exists;
- tests prove raw transaction description fields are not present;
- `make backend-check` passes.

## Slice 4 - Snapshot Service

Build:

- service that calls `prepare_pace_input_for_user(...)`;
- skips calculation when required inputs are missing;
- runs `calculate_pace(...)` when ready;
- builds snapshot JSON;
- inserts immutable snapshot;
- returns a typed outcome for route/dashboard use.

Triggers:

- `goal_created`;
- `goal_updated`;
- `financial_profile_updated`;
- `income_source_created`;
- `income_source_updated`;
- `income_source_deactivated`;
- `planned_expense_created`;
- `planned_expense_updated`;
- `planned_expense_deactivated`;
- `dashboard_opened` if we choose to allow explicit dashboard recalculation.

Success criteria:

- complete inputs create a snapshot;
- incomplete inputs return missing-input state and create no snapshot;
- unconfirmed reserve buffer blocks calculation;
- same valid inputs with the same calculation timestamp produce stable JSON;
- previous snapshot comparison sets previous snapshot id and weekly safe-to-spend delta;
- old snapshots are not modified after later input changes;
- `make backend-check` passes.

## Slice 5 - Input Write Integration

Build:

- connect valid goal and financial input writes to the snapshot service;
- update API responses only if needed to expose recalculation state;
- keep transaction commit behavior coherent: user input write and snapshot insert succeed or roll back together.

Success criteria:

- valid goal create/update creates a snapshot when all required inputs are complete;
- valid financial profile update creates a snapshot when all required inputs are complete;
- valid income/expense create/update/deactivation creates a snapshot when all required inputs are complete;
- invalid writes create no snapshot;
- missing-input writes create no snapshot but return useful setup state;
- `make backend-check` passes.

## Slice 6 - Dashboard and Latest Snapshot API

Build:

- `GET /api/v1/calculation-snapshots/latest`;
- `GET /api/v1/dashboard`;
- response schemas for latest snapshot and dashboard summary;
- route tests for auth, ownership, missing-input state, and successful dashboard data.

Success criteria:

- authenticated dashboard reads latest user-owned snapshot only;
- unauthenticated requests return `401`;
- missing setup returns missing-input details and does not present weekly safe-to-spend as valid;
- dashboard response includes goal summary, pace status, weekly safe-to-spend, shortfall, remaining weeks, progress percentage, formula version, and explanation payload;
- frontend-facing response comes from persisted snapshot/result JSON, not recalculating in the route;
- OpenAPI loads successfully;
- `make backend-check` passes.

## Slice 7 - Weekly Plan MVP Decision Point

If included in this phase, build:

- `WeeklyPlan` model and migration;
- repository for current week plan lookup/create;
- service logic that lazily creates the current local Monday-through-Sunday weekly plan on dashboard access when a latest snapshot exists;
- tests proving midweek recalculation does not replace the current week's opening allowance.

If deferred:

- dashboard response may set current-week opening allowance and remainder equal to latest weekly safe-to-spend for the backend-only MVP, with the limitation documented in this plan or a follow-up spec note.

Success criteria if included:

- one weekly plan per user/goal/week;
- `week_start` uses the user's local Monday;
- current week opening allowance is created from the latest snapshot once;
- midweek recalculation updates latest safe-to-spend but not current week opening allowance;
- `make backend-check` passes.

## Suggested Commit Breakdown

Preferred sequence:

1. `docs: add dashboard snapshots implementation plan`
2. `feat: add calculation snapshot model`
3. `feat: add calculation snapshot repository`
4. `feat: build calculation snapshot json`
5. `feat: add snapshot calculation service`
6. `feat: create snapshots after input changes`
7. `feat: add dashboard snapshot api`

Acceptable adjustments:

- combine repository and model work if the migration is small;
- split snapshot JSON builder from comparison logic if the tests become dense;
- defer weekly plans to a separate branch if the dashboard API can honestly represent missing weekly-plan state.

## Phase Completion Criteria

- Complete user inputs can produce an immutable `pace-v1` calculation snapshot.
- Incomplete inputs produce a missing-input state and no misleading safe-to-spend output.
- Latest dashboard data is served from backend snapshots.
- Snapshot JSON matches `snapshot-input-v1` and `snapshot-result-v1`.
- Old snapshots remain unchanged after current inputs mutate.
- The backend check suite passes.
