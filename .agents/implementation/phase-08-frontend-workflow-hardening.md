# Phase 8 - Frontend Workflow Hardening

## Purpose

Harden the already-wired frontend MVP workflow so it is reliable, demoable, and
clear.

The current frontend already calls backend APIs for account access, goal setup,
financial profile, income sources, planned expenses, dashboard data, and latest
snapshot data. This phase is not about "routing endpoints to the backend" from
scratch. It is about proving that wiring end-to-end, tightening weak UI states,
and correcting any product, accessibility, or data-flow gaps.

The target outcome is a browser demo where a new user can:

1. register or sign in;
2. create one active goal;
3. enter manual financial assumptions;
4. see backend-owned deterministic dashboard results;
5. inspect the latest immutable calculation snapshot.

## Source of Truth

- `CONTRIBUTING.md`
- `README.md`
- `ARCHITECTURE.md`
- `DESIGN.md`
- `docs/PRODUCT_CONTEXT.md`
- `docs/specs/0007-srs-traceability-and-mvp-scope.md`
- `docs/specs/0008-project-structure.md`
- `.agents/implementation/phase-07-frontend-foundation.md`
- backend schemas under `backend/app/schemas/`
- frontend API resources under `frontend/src/api/resources.ts`
- frontend routes under `frontend/src/routes/`

## Current Baseline

Already present:

- React + Vite app under `frontend/`;
- authenticated and unauthenticated route boundaries;
- backend API client using `fetch`, `credentials: "include"`, and CSRF headers
  for unsafe methods;
- register, login, logout, and `/me` session behavior;
- active goal create/update route;
- financial profile save route;
- income source create/update/delete route;
- planned expense create/update/delete route;
- dashboard route reading `GET /api/v1/dashboard`;
- calculation details route reading latest snapshot data;
- shared UI primitives for buttons, fields, panels, progress, alerts, empty
  states, and loading states.

Assumption to verify: saved browser changes persist because the frontend writes
through the FastAPI backend into the configured database, not because the UI uses
local-only persistence.

## Scope

In scope:

- end-to-end manual verification of persistence across reloads and restart where
  practical;
- frontend/backend contract audit for goal, financial profile, income source,
  planned expense, dashboard, and snapshot routes;
- first-run and missing-input flow cleanup;
- form validation and error display cleanup;
- loading, pending, success, empty, and destructive-action states;
- accessibility and responsive hardening for the primary MVP workflow;
- small component extraction if route files are carrying too much responsibility;
- focused tests where they reduce regression risk.

Out of scope:

- CSV import;
- transactions pages;
- AI summaries or AI classification;
- account export/delete;
- background scheduling UI;
- multiple active goals;
- frontend calculation of official financial values;
- production deployment.

## Architecture Checkpoint

The frontend data flow should remain:

```text
React route/component state
  -> frontend API resource function
  -> apiRequest()
  -> FastAPI /api/v1 endpoint
  -> backend service/repository
  -> database
  -> backend response
  -> React reload/render
```

React may format returned values for display. React must not duplicate
`pace-v1`, dashboard formulas, snapshot comparison logic, ownership checks, or
session/CSRF rules.

## Slice 1 - Persistence and Contract Audit

Verify:

- register/login creates a real backend session cookie and in-memory CSRF token;
- goal create/update persists after page reload;
- financial profile save persists after page reload;
- income source create/update/delete persists after page reload;
- planned expense create/update/delete persists after page reload;
- dashboard changes after valid backend recalculation;
- calculation snapshot appears after the backend has enough valid inputs.

Fix:

- stale TypeScript request/response types;
- endpoint path mismatches;
- incorrect enum labels or unsupported values;
- UI success copy that claims recalculation happened when the backend did not
  return enough evidence;
- API errors that collapse useful backend validation into vague generic text.

Success criteria:

- a newly registered user can complete the MVP setup path in the browser;
- reloading the page shows the saved backend state;
- frontend contracts match current backend schemas;
- no official financial output is computed in React.

## Slice 2 - First-Run and Missing-Input Flow

Build or refine:

- post-login/register landing behavior for users with no complete setup;
- dashboard missing-input cards that route to the exact setup screen needed;
- setup-to-dashboard navigation after successful saves;
- clear behavior when a user has a goal but incomplete financial assumptions;
- clear behavior when financial assumptions exist but no snapshot has been
  created yet.

Success criteria:

- the app does not strand first-time users on a dashboard that feels broken;
- every missing-input action links to a supported MVP route;
- no missing-input state points to deferred CSV, AI, transaction, or multi-goal
  features;
- success paths are predictable after save.

## Slice 3 - Form State and Validation Hardening

Build or refine:

- field-level display for backend `422` errors;
- form-level display for non-field API errors;
- submit disabled/loading states;
- reset/cancel behavior while editing income and expense rows;
- money input parsing and display behavior;
- date input defaults and invalid-date handling;
- delete/deactivate button states.

Success criteria:

- invalid backend responses are visible next to useful fields when possible;
- double-submit is prevented during pending saves;
- editing an existing row and canceling does not corrupt the create form;
- dollar inputs consistently convert to integer cents before API submission;
- date fields send ISO date-only values.

## Slice 4 - Dashboard and Snapshot Explanation Hardening

Build or refine:

- dashboard summary hierarchy for safe-to-spend, pace status, shortfall, goal
  progress, and current-week allowance;
- accessible progress semantics;
- snapshot trail section linking to calculation details;
- calculation details layout for formula version, trigger, timestamp,
  normalized input summary, and result summary;
- empty snapshot state when no snapshot exists yet.

Success criteria:

- dashboard values are all backend-provided;
- snapshot details are read-only and do not expose edit controls;
- no raw transaction descriptions or deferred transaction concepts appear;
- progress and status components are screen-reader understandable;
- mobile and desktop layouts are scannable.

## Slice 5 - Product Scope and Copy Cleanup

Audit:

- landing page CTAs;
- app shell navigation;
- dashboard panels;
- goal and financial input screen labels;
- snapshot explanation copy;
- empty/error/success states.

Fix:

- copy that implies unsupported current behavior;
- labels that sound like generic budgeting instead of one-goal planning;
- AI language that suggests AI calculates financial outputs;
- hidden or inert primary actions;
- confusing "delete" versus backend deactivation wording.

Success criteria:

- current MVP capabilities are represented accurately;
- deferred capabilities are absent or explicitly marked future-state only when
  intentionally shown;
- primary actions either perform real work or are visibly unavailable;
- the user can understand what the backend is the source of truth for.

## Slice 6 - Accessibility and Responsive Pass

Verify and fix:

- keyboard navigation through auth, goal, inputs, dashboard, and snapshot routes;
- focus visibility;
- form labels and error associations;
- progressbar `aria` values;
- contrast for status and error states;
- mobile width layout and horizontal overflow;
- text wrapping in buttons, panels, and summary strips.

Success criteria:

- primary MVP flow is keyboard usable;
- screen-reader semantics are present for forms, errors, loading, and progress;
- no incoherent overlap or horizontal scrolling in common mobile/desktop
  viewports;
- `make frontend-check` passes.

## Slice 7 - Focused Frontend Tests

Add tests only where they protect meaningful behavior:

- formatting and parsing helpers for cents/date display;
- API error normalization if not already covered;
- route/component behavior for critical forms if the test stack supports it;
- smoke coverage for dashboard missing-input rendering.

Success criteria:

- tests cover behavior likely to regress, not implementation details;
- checks remain fast enough for local development and CI;
- test fixtures do not introduce unsupported product capabilities.

## Suggested Commit Slices

Use small commits as work becomes real:

1. `docs: plan frontend workflow hardening`
2. `fix: align frontend contracts with backend schemas`
3. `fix: harden frontend setup flow`
4. `fix: improve financial input form states`
5. `fix: harden dashboard snapshot display`
6. `test: cover frontend workflow helpers`

Commit names can change based on the actual edits. Keep each commit focused on a
reviewable behavior change.

## Phase Completion Criteria

- The browser MVP flow works against the local backend and database.
- Saved goal and financial input data survive page reload.
- Dashboard and snapshot screens render backend-owned values only.
- First-run, missing-input, loading, validation, error, success, and pending
  states are clear.
- Frontend copy does not drift beyond MVP scope.
- Primary workflow passes accessibility and responsive smoke checks.
- Relevant frontend checks and focused tests pass.
