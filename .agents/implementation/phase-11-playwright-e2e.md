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

## Follow-up Slices

- Auth login and logout coverage.
- Complete first-run setup through goal, cash, income, and expenses.
- Replace free-form time-zone entry with a selectable time-zone control.
- Dashboard status scenarios using isolated seeded data.
- Archive flow and cross-user isolation.
- CI execution with an isolated test database.
