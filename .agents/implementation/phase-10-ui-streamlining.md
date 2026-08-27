# Phase 10 - UI Streamlining

## Purpose

Streamline the hosted GoalWise MVP so first-time users can complete the core
planning loop without facilitator explanation.

The app now has working backend persistence, deterministic dashboard results,
goal lifecycle support, and Railway staging deployment. This phase is not about
adding CSV import, runtime AI summaries, multi-goal support, or new financial
logic. It is about making the implemented MVP feel coherent, trustworthy, and
easy to operate.

The target outcome is a staged demo where a user can:

1. register or sign in;
2. understand what setup is missing;
3. create one active savings goal;
4. enter manual financial assumptions;
5. read the dashboard result;
6. inspect calculation details when they want evidence;
7. archive a goal without thinking they deleted history.

## Source of Truth

- `CONTRIBUTING.md`
- `README.md`
- `ARCHITECTURE.md`
- `DESIGN.md`
- `docs/PRODUCT_CONTEXT.md`
- `docs/srs/goal-wise-srs-v2.md`
- `docs/specs/0007-srs-traceability-and-mvp-scope.md`
- `docs/specs/0008-project-structure.md`
- `docs/specs/0009-ui-mockup-and-screenshot-workflow.md`
- `.agents/implementation/phase-08-frontend-workflow-hardening.md`
- `.agents/implementation/phase-09-goal-lifecycle-and-ui-polish.md`
- frontend routes under `frontend/src/routes/`
- frontend components under `frontend/src/components/`
- frontend API contracts under `frontend/src/api/`

## Current Baseline

Already present:

- authenticated app shell with dashboard, goal, inputs, and calculation routes;
- frontend API client using backend-owned values;
- register, login, logout, and authenticated route protection;
- goal create/update/archive flow;
- financial profile save flow;
- income source create/update/deactivate flow;
- planned expense create/update/deactivate flow;
- dashboard route reading backend `GET /api/v1/dashboard`;
- latest calculation route reading backend snapshot data;
- shared button, field, panel, progress, alert, empty-state, loading, and layout
  primitives;
- staging deployment with same-origin `/api/*` proxy through the frontend.

Known weak spots:

- the dashboard hierarchy still reads like implementation output instead of a
  user decision surface;
- first-run setup guidance is functional but not yet a guided workflow;
- financial input editing is dense and may be hard to scan on mobile;
- calculation details expose audit-oriented fields before user-oriented
  explanation;
- route files carry substantial UI responsibility;
- SRS v2 names an AI Future guardrail page while runtime AI remains deferred;
- frontend screenshots and usability evidence have not been refreshed after
  staging deployment.

## Scope

In scope:

- improve dashboard hierarchy, copy, and empty states;
- improve the goal setup and archive experience;
- improve financial input layout, edit states, and save feedback;
- improve calculation details as a trust/explanation surface;
- add or refine supported navigation only when backed by current routes or SRS
  guardrail requirements;
- extract small presentational components when route files become hard to
  reason about;
- responsive and accessibility pass for the primary MVP workflow;
- focused tests for behavior likely to regress.

Out of scope:

- CSV import;
- transaction correction or duplicate detection;
- runtime AI summaries or provider calls;
- AI-generated financial outputs;
- account export/delete;
- background scheduling controls;
- multiple active goals;
- frontend duplication of `pace-v1` formulas or official dashboard metrics.

## Architecture Checkpoint

The frontend must remain a renderer and workflow layer:

```text
React route/component state
  -> frontend API resource function
  -> apiRequest()
  -> same-origin /api/v1 request
  -> FastAPI endpoint
  -> backend service/repository
  -> database
  -> backend response
  -> React render
```

React may format cents, dates, percentages, labels, and loading states. React
must not calculate safe-to-spend, pace status, shortfall, current-week
allowance, snapshot comparisons, ownership checks, or CSRF/session rules.

## UI Direction

Use an "Operate" product UI mode:

- prioritize scanability, predictable controls, clear status hierarchy, and
  repeated task ergonomics;
- keep the UI calm and work-focused, not a marketing page inside the app;
- use status color for meaning, not decoration;
- prefer explicit user-facing language over internal terms such as raw snapshot
  JSON, input category keys, or backend implementation names;
- keep component vocabulary consistent across dashboard, goal setup, financial
  inputs, and calculation details.

## Options Considered

### Option A - Streamline the Existing MVP UI

Refine the current routes and components without changing backend contracts.

Tradeoffs:

- **Positive:** fastest path to a better staging demo; lowest risk to backend
  correctness; preserves current deployment and data flow.
- **Negative:** some route files may remain larger than ideal until targeted
  extraction happens.
- **Decision:** recommended for this phase.

### Option B - Extract a Full Design System First

Pause product work to build a larger component and token system before improving
screens.

Tradeoffs:

- **Positive:** creates stronger long-term consistency and reuse.
- **Negative:** delays visible usability improvements; risks abstracting before
  the actual screen needs are clear.
- **Decision:** reject for now. Extract only components proven useful by the
  streamlining work.

### Option C - Redesign Navigation Around Upcoming CSV and AI

Introduce future navigation for imports, transactions, AI summaries, and account
data rights now.

Tradeoffs:

- **Positive:** communicates the broader SRS direction.
- **Negative:** violates MVP clarity if future capabilities look available;
  increases reviewer confusion and implementation scope.
- **Decision:** reject for this phase. Future features may appear only as
  explicitly disabled guardrails when required by SRS v2.

## Slice 1 - Demo Journey Audit and UI Brief

Audit the current hosted/local UI against the three story users and the core
first-time setup path.

Assess:

- registration and login entry points;
- first dashboard load with no setup;
- goal setup;
- financial profile, income, and planned-expense entry;
- ready dashboard for `At Risk`, `On Track`, and `Off Pace` story states;
- calculation details;
- archive flow;
- logout and return.

Deliver:

- a short UI streamlining brief in this file or a companion note;
- a concrete issue list ordered by user impact;
- selected first coding slice.

Success criteria:

- every proposed UI change traces to a real screen, story user, SRS item, or
  current backend contract;
- no proposed change requires CSV import, runtime AI, export/delete, or
  multi-goal behavior;
- the first coding slice is small enough for one reviewable PR.

## Slice 2 - Dashboard Decision Surface

Refine the dashboard so the user's main question is answered first:

- "How much can I safely spend this week?"
- "Am I on pace?"
- "What changed or what should I fix next?"

Build or refine:

- safe-to-spend hero hierarchy;
- pace-status treatment for `Completed`, `Off Pace`, `Ahead`, `At Risk`, and
  `On Track`;
- current-week opening allowance and remainder;
- goal progress;
- missing-input action cards;
- links to goal, inputs, and calculation details;
- concise explanation of what data was included.

Success criteria:

- the dashboard is understandable in under one minute for each story user;
- all displayed financial outputs come from backend responses;
- no internal keys or unsupported features appear;
- mobile and desktop layouts remain scannable.

## Slice 3 - Setup Flow Guidance

Make the first-run path feel intentional instead of empty.

Build or refine:

- guided setup callouts that point users to the current goal, profile, income,
  expense, and dashboard steps;
- post-register/post-login routing for incomplete setup;
- dashboard missing-input sequence;
- setup progress affordance using only current MVP inputs;
- clear next action after saving a goal;
- clear next action after saving financial assumptions.

Success criteria:

- a first-time user always has one obvious next action;
- tutorial guidance is dismissible, mobile-safe, and not hover-only;
- no setup card points to deferred CSV, AI, export/delete, or multi-goal
  behavior;
- success messages do not promise a recalculation unless backend data supports
  it.

## Slice 4 - Financial Inputs Usability

Reduce cognitive load in the financial input screen.

Build or refine:

- financial profile section as the prerequisite for calculations;
- income and planned-expense sections as repeatable lists with edit/create
  states;
- clearer labels for confirmed versus unconfirmed income;
- clearer labels for essential versus discretionary expenses;
- pending, save, cancel, and deactivate states;
- mobile layout for dense forms and lists.

Success criteria:

- edit state is visibly distinct from create state;
- deactivation does not read as hard deletion;
- form errors are near the fields they affect;
- dollar inputs still convert to integer cents before API submission.

## Slice 5 - Calculation Details as Trust Surface

Make calculation details useful to a non-developer while preserving audit
evidence.

Build or refine:

- top summary of the latest calculation result;
- readable breakdown of included goal, profile, income, and expense assumptions;
- formula version and timestamp context;
- audit ID de-emphasized but available;
- read-only visual treatment.

Success criteria:

- a user can understand why the dashboard number exists;
- calculation records do not expose edit controls;
- raw normalized JSON and raw transaction descriptions are not shown;
- formula/version provenance remains available for review.

## Slice 6 - AI Future Guardrail Page

SRS v2 includes a current Must requirement for an AI Future guardrail while
runtime AI provider behavior remains future scope.

Build or refine only if we choose to satisfy that SRS v2 UI requirement now:

- a route or panel that explains AI summaries are not enabled in the current
  MVP;
- explicit statement that AI does not calculate safe-to-spend, pace status,
  shortfall, or stored inputs;
- no external provider calls;
- no fake summaries.

Success criteria:

- feature flag disabled means zero AI calls;
- the page cannot be confused with an enabled AI summary feature;
- MVP scope mapping is updated if implementation status changes.

## Slice 7 - Responsive and Accessibility Pass

Verify and fix:

- keyboard navigation through auth, dashboard, goal, inputs, calculation, and
  archive flows;
- visible focus;
- labels and error associations;
- progressbar semantics;
- color contrast for status/error/success states;
- mobile width layout and horizontal overflow;
- text wrapping in cards, panels, and buttons.

Success criteria:

- primary MVP flow is keyboard usable;
- screen-reader semantics are present for forms, errors, loading, and progress;
- no incoherent overlap or horizontal scrolling in common mobile and desktop
  viewports;
- `make frontend-check` passes.

## Slice 8 - Focused Frontend Tests and Evidence

Add or update tests only where they protect meaningful behavior:

- status label and formatting helpers;
- dashboard missing-input rendering if supported by the current test stack;
- API error handling for user-facing failures;
- component behavior for edit/cancel/deactivate states if practical.

Capture evidence:

- local or staging smoke checklist results;
- screenshots only after UI is polished enough to be useful.

Success criteria:

- tests protect behavior, not incidental markup;
- checks remain fast;
- screenshots do not present unsupported future features as current behavior.

## Slice 9 - Cached Frontend Data Loading

Reduce route-to-route loading flashes without moving financial logic into the
frontend.

Build or refine:

- shared frontend query provider;
- cached query hooks for active goal, financial inputs, dashboard, and latest
  calculation snapshot;
- cache invalidation after goal and financial-input writes;
- session-boundary cache clearing on login, register, and logout;
- route loading behavior that still shows first-load and error states clearly.

Success criteria:

- revisiting Goal, Financial Inputs, Dashboard, and Calculation Details can use
  cached data instead of full-page loading flashes;
- saved changes refresh the affected dashboard and calculation-detail data;
- cached private data is cleared when the authenticated user changes;
- backend remains the source of truth for all financial outputs.

## Suggested Commit Slices

1. `docs: plan ui streamlining phase`
2. `fix: clarify dashboard decision hierarchy`
3. `fix: guide first-run setup flow`
4. `fix: streamline financial input editing`
5. `fix: improve calculation explanation view`
6. `feat: add ai future guardrail page`
7. `fix: harden responsive accessibility states`
8. `test: cover streamlined frontend behavior`
9. `feat: cache frontend route data`

## Phase Completion Criteria

- A new user can complete the MVP workflow without facilitator explanation.
- Story users with `At Risk`, `On Track`, and `Off Pace` states are clear on the
  dashboard.
- Frontend displays backend-owned financial values only.
- Deferred CSV import, runtime AI summaries, export/delete, scheduler, and
  multi-goal behavior are not represented as working features.
- SRS v2 UI guardrail obligations are either implemented or explicitly deferred
  in scope docs.
- `make frontend-check` passes.
