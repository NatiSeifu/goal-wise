# Phase 4 - Goals and Financial Inputs

## Purpose

Implement the backend MVP resources that let an authenticated user define one active savings goal and the financial assumptions needed by the deterministic pace engine.

This is an execution plan, not a new implementation contract. The source of truth remains:

- `docs/specs/0002-api-response-conventions.md`
- `docs/specs/0003-pace-engine-behavior.md`
- `docs/specs/0004-snapshot-json-schema.md`
- `docs/specs/0005-date-time-semantics.md`
- `docs/specs/0008-project-structure.md`
- `docs/adr/0001-layered-modular-monolith.md`
- `docs/adr/0004-money-integer-cents-and-formula-versioning.md`
- `docs/adr/0005-auth-sessions-and-ownership.md`
- `docs/adr/0006-versioned-rest-api.md`
- `.agents/plans/02-goal-and-financial-inputs.md`

## Scope

In scope:

- persistence models and migrations for goals and manual financial inputs;
- user-owned repositories for goal, profile, income, and planned-expense records;
- service-layer validation for money, dates, ownership, and lifecycle rules;
- Pydantic schemas for request and response payloads;
- versioned REST routes under `/api/v1`;
- CSRF protection for state-changing authenticated requests;
- focused unit, repository, and API tests.

Out of scope:

- frontend forms;
- CSV transaction import;
- accepted transaction persistence;
- dashboard response composition;
- calculation-snapshot creation;
- weekly plan creation;
- optional AI summaries or transaction classification.

## Design Direction

Use the existing layered backend shape:

```text
API route -> schema validation -> service -> repository -> SQLAlchemy model
```

Default MVP data shape:

- `Goal` stores the single active goal and preserved completed/archived goal history.
- `FinancialProfile` stores user-level cash baseline and confirmed reserve buffer.
- `IncomeSource` stores recurring or one-time expected income.
- `PlannedExpense` stores recurring or one-time expected expenses.

This keeps the records aligned with the pace engine inputs and the snapshot schema. It also avoids compressing all financial assumptions into one JSON profile, which would make validation, ownership checks, updates, and future transaction insights harder to test.

## Decisions to Discuss Before Coding

- Endpoint shape: keep the plan's resource endpoints, or simplify some routes around "current" resources.
- Update behavior: use `PATCH` for partial goal updates and `PUT` for full financial profile replacement, as currently planned.
- Deactivation behavior: soft-deactivate income and planned expenses for MVP traceability instead of hard delete.
- Missing-input responses: decide the exact response shape for missing active goal or missing financial profile.
- Recalculation hook timing: this phase can expose a service seam for recalculation, but snapshot creation should remain in a later dashboard/snapshot phase unless pulled forward.

## Slice 1 - Persistence Models and Migration

Build:

- `backend/app/models/goal.py`;
- `backend/app/models/financial_profile.py`;
- `backend/app/models/income_source.py`;
- `backend/app/models/planned_expense.py`;
- Alembic migration for the new tables;
- model metadata imports.

Suggested fields:

- `Goal`: `id`, `user_id`, `name`, `target_cents`, `initial_saved_cents`, `current_saved_cents`, `start_date`, `target_date`, `status`, `archived_at`, `created_at`, `updated_at`.
- `FinancialProfile`: `id`, `user_id`, `starting_cash_cents`, `balance_as_of_date`, `reserve_buffer_cents`, `reserve_buffer_confirmed`, `created_at`, `updated_at`.
- `IncomeSource`: `id`, `user_id`, `name`, `amount_cents`, `next_date`, `frequency`, `confidence`, `active`, `created_at`, `updated_at`.
- `PlannedExpense`: `id`, `user_id`, `name`, `amount_cents`, `next_date`, `frequency`, `classification`, `active`, `created_at`, `updated_at`.

Success criteria:

- all user-owned tables have `user_id` foreign keys;
- money fields are integer cents;
- enum-like values are stored as strings;
- date-only values use SQLAlchemy date columns;
- timestamps use existing UTC conventions;
- one active goal per user is enforced by service logic and supported by an index where portable;
- migration upgrades and downgrades in SQLite tests;
- `make backend-check` passes.

## Slice 2 - Repository Layer

Build:

- goal repository methods for active lookup, create, owned lookup, update, and lifecycle changes;
- financial profile repository methods for current lookup and upsert;
- income-source repository methods for list, create, owned lookup, update, and deactivate;
- planned-expense repository methods for list, create, owned lookup, update, and deactivate.

Success criteria:

- every private query filters by authenticated `user_id`;
- cross-user lookup behaves like missing data;
- list endpoints return only active records unless explicitly designed otherwise;
- repositories contain SQLAlchemy query behavior, not business validation;
- repository tests cover owned access and cross-user isolation;
- `make backend-check` passes.

## Slice 3 - Service Validation

Build:

- goal service behavior for create, active lookup, update, complete, and archive paths;
- financial profile service behavior for create/replace;
- income-source service behavior;
- planned-expense service behavior;
- shared validation helpers only if duplication becomes meaningful.

Validation rules:

- target amount must be greater than zero;
- current saved amount cannot be negative or greater than target amount;
- target date must be later than the user's current local date;
- starting cash cannot be negative for MVP;
- balance-as-of date cannot be in the future;
- money is normalized to integer cents before persistence;
- names have bounded lengths;
- allowed frequencies are `one_time`, `weekly`, `biweekly`, and `monthly`;
- allowed income confidence values are `confirmed` and `unconfirmed`;
- allowed expense classifications are `essential` and `discretionary`;
- first financial profile setup suggests a reserve buffer equal to 5% of confirmed future income rounded up to the nearest whole U.S. dollar, with `$0` allowed when confirmed future income is zero;
- first valid pace calculation remains blocked until the reserve buffer is confirmed or replaced.

Success criteria:

- services receive authenticated user id explicitly;
- services never trust `user_id` from request bodies;
- date validation uses the user's IANA time zone;
- completed, archived, and active lifecycle states stay separate from calculated `pace_status`;
- validation failures map cleanly to API errors;
- `make backend-check` passes.

## Slice 4 - API Schemas and Routes

Build:

- goal schemas and `/api/v1/goals` routes;
- financial profile schemas and `/api/v1/financial-profile` routes;
- income-source schemas and `/api/v1/income-sources` routes;
- planned-expense schemas and `/api/v1/planned-expenses` routes;
- route registration through the existing v1 router.

Planned endpoints:

- `GET /api/v1/goals/active`;
- `POST /api/v1/goals`;
- `PATCH /api/v1/goals/{goal_id}`;
- `GET /api/v1/financial-profile`;
- `PUT /api/v1/financial-profile`;
- `GET /api/v1/income-sources`;
- `POST /api/v1/income-sources`;
- `PATCH /api/v1/income-sources/{income_source_id}`;
- `DELETE /api/v1/income-sources/{income_source_id}`;
- `GET /api/v1/planned-expenses`;
- `POST /api/v1/planned-expenses`;
- `PATCH /api/v1/planned-expenses/{planned_expense_id}`;
- `DELETE /api/v1/planned-expenses/{planned_expense_id}`.

Success criteria:

- safe reads require a valid authenticated session;
- state-changing routes require valid session and CSRF dependencies;
- missing private resources and cross-user access return `404`;
- unauthenticated requests return `401`;
- validation errors return `422` with field-level details;
- OpenAPI loads successfully;
- `make backend-check` passes.

## Slice 5 - Recalculation Boundary

Build:

- a small service-level recalculation hook or placeholder interface that can be called after valid input changes;
- tests proving input writes call or skip the hook as intended without requiring snapshot persistence yet.

Success criteria:

- complete inputs can be normalized for the pace engine later;
- incomplete inputs return a missing-input state rather than creating snapshots;
- snapshot creation remains isolated for the later dashboard/snapshot phase;
- the hook does not make routes depend directly on pace-engine internals;
- `make backend-check` passes.

## Slice 6 - API Security and Contract Tests

Build tests proving:

- authenticated users can create and update their own active goal;
- a second active goal is rejected;
- completed or archived goals are not returned as active;
- authenticated users can create/replace financial profile data;
- income sources and planned expenses can be created, updated, listed, and deactivated;
- deactivated income and expenses are excluded from active lists;
- unsafe endpoints reject missing or invalid CSRF tokens;
- cross-user reads and writes return `404`;
- malformed money, date, frequency, confidence, and classification inputs are rejected.

Success criteria:

- tests use isolated SQLite databases;
- tests do not require network access;
- tests exercise the public API shape, not just service internals;
- `make backend-check` passes.

## Suggested Commit Breakdown

Preferred sequence:

1. `docs: add goals and financial inputs implementation plan`
2. `feat: add goal and financial input models`
3. `feat: add goal and financial input repositories`
4. `feat: add goal and financial input services`
5. `feat: add goal and financial input api routes`
6. `test: cover goal and financial input api behavior`

Acceptable adjustments:

- combine model and repository slices if the migration is small;
- split income-source and planned-expense work if the review becomes too large;
- defer the recalculation hook if dashboard/snapshot work is intentionally kept in a separate branch.

## Phase Completion Criteria

- A signed-in user can manage the MVP goal and financial assumptions through `/api/v1`.
- All user-owned records are isolated by authenticated user id.
- Money is persisted only as integer cents.
- Date-only fields follow user-local date semantics.
- The stored records can be normalized into the accepted `pace-v1` input shape.
- The backend check suite passes.
