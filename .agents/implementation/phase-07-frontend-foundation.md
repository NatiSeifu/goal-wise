# Phase 7 - Frontend Foundation and Composable UI

## Purpose

Create the production React frontend foundation for GoalWise without prematurely
locking the final visual design. The frontend should be ready to consume the
FastAPI backend, render backend-owned financial outputs, and evolve from the
mockup direction into maintainable screens.

This phase is about frontend structure, contracts, routing, and reusable UI
building blocks. It should not duplicate pace-engine formulas or invent product
capabilities beyond the current MVP scope.

Source of truth:

- `CONTRIBUTING.md`
- `README.md`
- `ARCHITECTURE.md`
- `DESIGN.md`
- `docs/PRODUCT_CONTEXT.md`
- `docs/specs/0007-srs-traceability-and-mvp-scope.md`
- `docs/specs/0008-project-structure.md`
- `docs/specs/0009-ui-mockup-and-screenshot-workflow.md`
- Backend API schemas under `backend/app/schemas/`

Visual reference:

- `/Users/nati/worktrees/goal-wise-mockups/mockups`

The mockup worktree is a visual and interaction reference, not a production code
source. Preserve the product direction, but rebuild the frontend as composable
production code.

## Scope

In scope:

- React + Vite frontend scaffold under `frontend/`;
- TypeScript configuration and package scripts;
- app routing and authenticated/unauthenticated route boundaries;
- backend API client with cookie credentials and CSRF header support;
- typed frontend representations of current backend response/request contracts;
- reusable UI primitives and style tokens;
- route-level placeholders or thin screens that map to current MVP flows;
- accessibility baseline for navigation, buttons, forms, progress, loading,
  empty, and error states;
- CI/local commands for frontend build and checks.

Out of scope:

- final high-fidelity dashboard polish before teammate mockups are approved;
- CSV import, transaction pages, AI summaries, export/delete, scheduler, and
  multi-goal behavior;
- frontend recalculation of official financial metrics;
- production deployment of the frontend;
- broad design-system package extraction.

## Design Direction

Use the mockup's strongest product ideas:

- left-sidebar app shell for authenticated app screens;
- goal-first dashboard hierarchy;
- calm green/blue financial trust palette;
- summary metrics above detailed plan content;
- clear status treatments for safe-to-spend, pace status, shortfall, and
  snapshots;
- explicit AI boundary copy when future AI concepts appear.

Do not carry over the mockup's brittle implementation choices:

- no single 500+ line `App.tsx`;
- no query-param screen router as the production routing model;
- no inert primary CTAs;
- no progress visuals without accessible progress semantics;
- no unsupported navigation items or deferred features shown as current MVP.

## Architecture Variants

### Option A - Vite app with local CSS tokens and composable components

Build a Vite React app with plain TypeScript, React Router, local CSS tokens,
shared components, and feature folders.

Trade-offs:

- Positive: smallest dependency surface, easy to understand, aligns with the
  accepted `frontend/` structure, and keeps style replacement possible.
- Positive: avoids committing too early to a third-party component system while
  teammate mockups are still evolving.
- Negative: we must build enough primitives ourselves: buttons, fields, layout,
  progress, alerts, and cards.

Recommendation: use this for the first frontend phase.

### Option B - Tailwind-first frontend

Use Tailwind utility classes for fast layout and token iteration.

Trade-offs:

- Positive: fast to iterate and common for React/Vite apps.
- Negative: visual choices can scatter across route files unless we enforce
  component boundaries carefully.
- Negative: replacing the style system later can be more tedious if screens are
  utility-heavy.

Use only if the team wants Tailwind as an explicit frontend convention.

### Option C - Component library first

Adopt a prebuilt component library for forms, modals, navigation, and a11y
behavior.

Trade-offs:

- Positive: can speed up accessibility and interaction details.
- Negative: introduces a visual and API commitment before the app's design
  language is settled.
- Negative: may fight the custom dashboard and finance-specific hierarchy.

Defer until a repeated need appears.

## Target Frontend Structure

Follow `SPEC-0008`:

```text
frontend/
  src/
    app/
      App.tsx
      router.tsx
      providers.tsx
    api/
      client.ts
      errors.ts
      types.ts
    components/
      ui/
      layout/
      feedback/
    features/
      auth/
      dashboard/
      goal/
      financial-profile/
      income-sources/
      planned-expenses/
      calculation-snapshots/
    routes/
    styles/
      tokens.css
      global.css
    utils/
```

Screens should compose feature components and shared primitives. Feature modules
may own workflow-specific components, hooks, and formatters. Shared components
must stay generic.

## Mockup Review Findings To Carry Forward

The existing mockup is visually useful, but production frontend work must fix:

- Primary CTAs must navigate, submit, or be explicitly disabled with demo copy.
- The landing `Security` link must target a real `id` or be removed.
- Progress bars must expose `role="progressbar"`, `aria-valuemin`,
  `aria-valuemax`, `aria-valuenow`, and an accessible label.
- `App.tsx` responsibilities must be split into app setup, routes, feature
  screens, shared components, and mock/fixture data.

## Slice 1 - Frontend Scaffold and Tooling

Build:

- `frontend/` Vite React + TypeScript app;
- package scripts for dev, build, lint/typecheck if selected;
- root `Makefile` targets for frontend setup/checks;
- basic `frontend/README.md`;
- no production UI beyond a minimal route shell.

Success criteria:

- `frontend/` builds from the repo root command;
- tooling does not depend on global Node state beyond the package manager;
- generated files, caches, and local env files are ignored;
- root/backend workflows are not broken.

## Slice 2 - App Routing and Layout Boundary

Build:

- route definitions for current MVP surfaces;
- landing route;
- authenticated app shell route group;
- placeholder routes for dashboard, goal setup, financial inputs, calculation
  details, login, and register;
- real links instead of inert CTAs.

Success criteria:

- all visible navigation and primary CTAs go somewhere real or are explicitly
  disabled;
- no route presents deferred capabilities as current behavior;
- route modules are small and composable;
- mobile and desktop navigation do not overflow.

## Slice 3 - API Client and Contract Types

Build:

- centralized API client for `/api/v1`;
- `credentials: "include"` on authenticated requests;
- CSRF token storage and `X-CSRF-Token` on unsafe authenticated methods;
- normalized API error shape for UI;
- TypeScript interfaces matching current backend schemas.

Success criteria:

- frontend API code does not calculate official financial outputs;
- endpoint paths are centralized;
- auth/session behavior matches backend CSRF/session choices;
- contract types cover auth, goal, financial profile, income sources, planned
  expenses, dashboard, and calculation snapshots.

## Slice 4 - Auth Flow Skeleton

Build:

- register, login, logout, and `/me` session check wiring;
- auth state provider or equivalent lightweight state boundary;
- protected route behavior;
- loading and unauthenticated states.

Success criteria:

- login/register use backend responses and CSRF token correctly;
- logout uses CSRF protection;
- protected routes redirect or show the correct unauthenticated state;
- no sensitive token is stored in local storage.

## Slice 5 - Dashboard Data Shell

Build:

- dashboard route that consumes `GET /api/v1/dashboard`;
- latest snapshot route/panel that consumes snapshot API data;
- accessible progress and status components;
- loading, missing-inputs, empty, and error states.

Success criteria:

- safe-to-spend, pace status, shortfall, progress, formula version, and snapshot
  data come from backend response fields;
- frontend formats integer cents but does not recompute metrics;
- missing input states guide the user to supported MVP setup screens;
- all progress visuals have accessible progress semantics.

## Slice 6 - Goal and Financial Input Forms

Build:

- current active goal form;
- financial profile form;
- income source list/create/update/deactivate or delete flow;
- planned expense list/create/update/deactivate or delete flow;
- field-level validation display from backend `422` responses.

Success criteria:

- forms submit to backend APIs and render returned data;
- successful writes trigger backend recalculation through existing endpoints;
- validation messages map to fields where possible;
- date and money inputs are formatted for users but sent in backend contract
  shape.

## Slice 7 - Visual System Pass

Build:

- style tokens for color, spacing, typography, radius, elevation, focus, and
  status tones;
- reusable Button, Field, Card/Panel, Progress, Alert, EmptyState, and AppShell
  primitives;
- mockup-inspired but production-clean dashboard composition;
- screenshot verification across desktop and mobile.

Success criteria:

- styles are centralized enough to replace or retheme without rewriting feature
  screens;
- no UI cards nested inside page-section cards;
- controls have visible focus states and semantic roles;
- text does not overlap or overflow in mobile/desktop screenshots;
- design matches product truth and does not invent unsupported features.

## Slice 8 - Frontend CI

Build:

- GitHub Actions frontend checks;
- local root command alignment;
- frontend build verification on PRs to `development`.

Success criteria:

- frontend CI runs only when relevant frontend/workflow files change;
- backend CI remains unchanged;
- checks do not require secrets.

## Open Decisions Before Slice 1

- Package manager: `npm` is simplest because the mockup already uses it; `pnpm`
  is also reasonable if the team wants stricter installs.
- Router: React Router is the likely default for this client-rendered Vite app.
- Type strategy: handwritten TypeScript interfaces first, or generate from
  FastAPI OpenAPI after the API stabilizes further.
- Styling: start with CSS tokens/modules/plain CSS, or adopt Tailwind now.
- Test stack: Vitest + React Testing Library for unit/component tests, with
  Playwright added when full browser flows matter.

## Phase Completion Criteria

- `frontend/` exists and follows `SPEC-0008`.
- The app can build locally.
- MVP routes exist and are navigable.
- Frontend API client can call backend with cookies and CSRF correctly.
- Dashboard and input flows consume backend contracts without duplicating
  financial formulas.
- Core UI primitives are reusable and style tokens are centralized.
- Accessibility issues from the mockup review are fixed in production code.
- Frontend checks are documented and, when added, run in CI.
