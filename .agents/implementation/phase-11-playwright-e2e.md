# Phase 11 - Playwright End-to-End Foundation

## Purpose

Add a small browser-level test layer for the real React and FastAPI application.
The suite will protect user journeys and backend integration without replacing
the existing Vitest frontend tests or pytest backend tests.

## Scope

The first slice covers:

- local-only Playwright configuration;
- Chromium as the initial browser project;
- a unique test-user strategy;
- registration and authenticated route navigation;
- the shared setup guide path from registration to Dashboard;
- failure screenshots, traces, and an HTML report for diagnosis.

The suite must never target staging or production by default. It requires the
local backend at `http://127.0.0.1:8000` and the local frontend at
`http://localhost:5173`.

## Slice 1 - Browser Test Foundation

### Implementation

- Add `@playwright/test` to the frontend development dependencies.
- Add `frontend/playwright.config.ts` with a local Vite web server, Chromium,
  stable timeouts, and failure artifacts.
- Add `frontend/e2e/auth-and-setup.spec.ts`.
- Add an npm script for running the suite.
- Use accessible roles and labels first; add test IDs only when a stable
  user-facing locator is not available.

### Test journey

1. Register a unique local test user.
2. Verify the app routes the user to Goal setup.
3. Verify the setup guide is visible and its Dashboard card is navigable.
4. Navigate to Dashboard and verify the authenticated setup state is shown.

### Success criteria

- The test passes against the local backend and frontend.
- The test does not use staging or production data.
- The test uses browser-visible behavior rather than implementation selectors.
- Existing `make frontend-check` remains green.

## Slice 2 - Authentication Journey

### Test journey

1. Register a unique local test user.
2. Sign out from the authenticated app shell.
3. Confirm a protected route redirects to Sign in.
4. Sign in with the registered credentials.
5. Confirm the authenticated Dashboard is available again.

### Success criteria

- Login and logout are verified through the browser UI.
- Logout removes access to protected routes.
- The test remains isolated from other test users.
- Slice 1 and the existing frontend checks remain green.

## Slice 3 - Complete First-Run Setup

### Test journey

1. Register a unique local test user.
2. Create a savings goal with a future target date.
3. Save starting cash, balance date, and a confirmed reserve buffer.
4. Add one confirmed income source and one essential planned expense.
5. Open Dashboard and verify the backend returns a ready planning result.

### Success criteria

- The complete first-run setup is verified through the browser UI.
- The Dashboard displays a backend-owned weekly safe-to-spend result.
- The test uses dates relative to the current browser date.
- Slice 2 and the existing frontend checks remain green.

## Slice 4 - Selectable Time Zone

### Implementation

- Replace free-form registration time-zone entry with a native accessible select.
- Preserve browser detection when the detected zone is supported.
- Use a safe default when browser detection is unavailable or unsupported.
- Update browser registration journeys to select the time zone.

### Success criteria

- Registration submits a valid IANA time-zone value selected from the UI.
- The control is keyboard and screen-reader accessible.
- Existing E2E and frontend checks remain green.

## Slice 5 - Dashboard Status Scenarios

### Implementation

- Add reusable browser flows for registration and first-run setup.
- Add isolated scenarios for each supported pace status.
- Verify the Dashboard status treatment and core decision-surface values.

### Success criteria

- `Off Pace`, `Ahead`, `At Risk`, and `On Track` are each covered in the active
  Dashboard flow. `Completed` remains covered by pace-engine tests because the
  backend marks a completed goal inactive for Dashboard purposes.
- Every scenario uses a fresh user and supported MVP inputs.
- Assertions focus on backend-owned status and rendered decision-surface content.
- Existing E2E and frontend checks remain green.

## Slice 6 - Goal Lifecycle and User Isolation

### Test journey

1. Register a user and create an active goal.
2. Archive the goal through the Goal setup UI.
3. Confirm the active goal is cleared and a new goal can be created.
4. Register a second user in a separate browser context.
5. Attempt to archive User A's goal as User B and verify the API returns `404`.

### Success criteria

- Archive behavior is verified through the browser UI.
- Archived goals are removed from active planning without being deleted.
- A new active goal can be created after archival.
- Cross-user mutation is rejected with the existing `404` contract.
- Existing E2E and frontend checks remain green.

## Slice 7 - CI Execution With an Isolated Test Database

### Implementation

- Add a dedicated GitHub Actions frontend E2E job.
- Provision a fresh PostgreSQL service for each workflow run.
- Apply Alembic migrations before starting the API.
- Run the real FastAPI service and Vite frontend under Playwright.
- Upload Playwright reports, screenshots, traces, videos, and API logs as
  workflow artifacts when the job completes.
- Retain artifacts for a short diagnostic window without committing them.

### Success criteria

- Pull requests that change frontend, workflow, or Makefile files run the E2E job.
- The E2E job uses only CI-local database credentials and test data.
- Migrations, API startup, and all browser tests pass in GitHub Actions.
- A failed browser test leaves enough report and trace data to diagnose it from
  the workflow run's artifact section.
- The job does not target staging or production.

## Completion

Phase 11 is complete when Slice 7 is implemented. No additional slices are
currently planned for this phase.
