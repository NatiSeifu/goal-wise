# Phase 1 - Deterministic Pace Engine

## Purpose

Build the pure `pace-v1` calculation engine before adding persistence, API routes, auth, or frontend behavior.

This is an execution plan, not a new implementation contract. The source of truth remains:

- `docs/specs/0003-pace-engine-behavior.md`
- `docs/specs/0005-date-time-semantics.md`
- `docs/adr/0002-deterministic-pace-engine-no-runtime-ai.md`
- `docs/adr/0004-money-integer-cents-and-formula-versioning.md`
- `docs/specs/0008-project-structure.md`

## Scope

In scope:

- pure Python pace engine types;
- `pace-v1` formula implementation;
- named synthetic golden fixtures;
- unit tests and architecture-boundary tests for the engine.

Out of scope:

- FastAPI routes;
- SQLAlchemy models;
- repositories;
- auth/session logic;
- calculation snapshots;
- weekly plan persistence;
- React UI;
- runtime AI summaries or AI classification.

## Slice 1 - Define Engine Contract

Build:

- `backend/app/pace_engine/types.py`
- normalized input type for calculation data;
- result type for calculation outputs;
- enums for goal lifecycle status, pace status, income confidence, expense classification, and recurrence frequency;
- formula version constant: `pace-v1`.

Success criteria:

- types are pure Python and import no FastAPI, SQLAlchemy, repository, auth/session, frontend, or AI modules;
- all money fields are integer cents;
- date-only fields use `datetime.date`;
- calculation timestamp uses timezone-aware `datetime`;
- result type includes required intermediate and final output fields from `SPEC-0003`;
- `make backend-check` passes.

## Slice 2 - Add Synthetic Golden Fixtures

Build:

- `backend/tests/pace_engine/fixtures.py`;
- named scenarios with input and expected output.

Required scenarios:

- `completed`;
- `off_pace`;
- `ahead`;
- `at_risk`;
- `on_track`;
- `zero_confirmed_future_income`;
- `fewer_than_seven_days_remaining`;
- `unconfirmed_income_excluded`;
- `rounding_down_to_whole_dollars`.

Success criteria:

- fixtures are named by behavior, not by arbitrary numbers;
- each fixture includes input and expected output;
- expected values are manually reviewable;
- fixtures do not depend on database, FastAPI, or frontend code;
- `make backend-check` passes.

## Slice 3 - Implement Core Formula Helpers

Build helper functions for:

- confirmed future income;
- planned future expenses;
- forecast resources;
- goal gap;
- discretionary capacity;
- remaining weeks;
- weekly safe-to-spend;
- projected shortfall.

Success criteria:

- helper functions are deterministic and side-effect free;
- helpers do not mutate input data;
- all money math uses integer cents;
- same-day income and expense occurrences are excluded from future forecasts;
- income and expense occurrences after the target date are excluded;
- weekly safe-to-spend rounds down to whole U.S. dollars;
- `make backend-check` passes.

## Slice 4 - Implement Reserve Buffer Suggestion

Build:

- function for suggested reserve buffer;
- confirmed-future-income-only calculation;
- 5% rounded upward to the nearest whole dollar;
- `$0` suggestion when confirmed future income is zero.

Success criteria:

- unconfirmed income is excluded;
- nonzero suggestions round up to whole-dollar cents;
- zero confirmed future income returns `0`;
- function does not silently change an already confirmed user-provided reserve buffer;
- tests cover zero and nonzero confirmed income;
- `make backend-check` passes.

## Slice 5 - Implement Pace Status Decision Tree

Build:

- expected-savings-to-date calculation;
- tolerance calculation: `max($25, 5% of target amount)`;
- pace status evaluator.

Status evaluation order:

1. `Completed`
2. `Off Pace`
3. `Ahead`
4. `At Risk`
5. `On Track`

Success criteria:

- status order matches `SPEC-0003`;
- `Completed` overrides all other statuses;
- `Off Pace` overrides ahead/at-risk/on-track when forecast resources are below goal gap;
- `Ahead` and `At Risk` use the tolerance value;
- tests prove every status branch;
- `make backend-check` passes.

## Slice 6 - Implement Public Calculate Function

Build:

- `calculate_pace(inputs) -> PaceResult`;
- internal calls to the formula helpers;
- result assembly with formula version and all required values.

Success criteria:

- full golden scenarios pass;
- identical inputs return equal results;
- result includes intermediate values, not only weekly safe-to-spend;
- no runtime AI or external provider dependency exists;
- `make backend-check` passes.

## Slice 7 - Add Boundary and Determinism Tests

Build tests that assert:

- `pace_engine` imports no forbidden modules;
- `calculate_pace` is deterministic for identical normalized inputs;
- all golden fixtures pass.

Forbidden dependency categories:

- FastAPI;
- SQLAlchemy;
- repositories;
- auth/session modules;
- frontend modules;
- AI provider modules.

Success criteria:

- boundary test fails if `pace_engine` imports forbidden dependencies;
- determinism test proves equivalent input produces equivalent output;
- all golden fixtures pass;
- `make backend-check` passes.

## Suggested PR Breakdown

Preferred sequence:

1. `feat: define pace engine contract`
2. `feat: implement pace engine calculations`
3. `test: add pace engine golden scenarios`

Acceptable faster sequence:

- one focused Phase 1 PR with internal commits in the same order as the slices above.

## Phase Completion Criteria

Phase 1 is complete when:

- `backend/app/pace_engine/` contains the pure engine contract and implementation;
- `backend/tests/pace_engine/` contains named golden fixtures and tests;
- tests cover every required scenario listed in this plan;
- forbidden dependency tests pass;
- deterministic repeatability tests pass;
- `make backend-check` passes;
- no FastAPI, SQLAlchemy, auth/session, repository, frontend, or AI code is required to run the engine.
