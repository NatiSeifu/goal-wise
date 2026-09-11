# SPEC-0012: UI Content and Hierarchy

Status: Accepted
Last Updated: 2026-09-09
Related ADRs: ADR-0008
Related Specs: SPEC-0007, SPEC-0009, SPEC-0011

## Purpose

Keep the operational UI focused on the user's plan and available actions. Remove
product narration, repeated metrics, coaching panels, and walkthroughs that
repeat visible controls. This is a presentation change within the existing MVP;
it does not change API contracts, financial formulas, or authentication.

## Content rules

- Headings name the screen or data. Do not add slogans, eyebrow labels, or a
  paragraph explaining an otherwise self-explanatory form.
- Keep field labels, validation errors, saving states, and brief save receipts.
- Keep guidance that prevents a specific mistake: cash excludes goal savings,
  initial and current savings differ, reserve is excluded from spending,
  unconfirmed income is excluded, and passwords require 12 characters.
- Keep the import's supported file format and explicit replacement warning.
- Do not expose engineering terms such as MVP, deterministic core, or snapshot
  provenance in the main task flow.

## Screens and actions

| Screen | Visible content and actions |
| --- | --- |
| Landing | One purpose statement, short input summary, create account, sign in. |
| Sign in / register | Labeled account fields, submit action, account switch link, validation. |
| Goal | Savings target, savings and dates fields, save/create, expandable archive action when applicable, links to inputs and dashboard. No setup guide or duplicate saved-goal summary. |
| Financial inputs | Cash and reserve form; saved income and expense lists with expandable add/edit forms; edit/remove actions; dashboard link. No step walkthrough or coaching cards. |
| Dashboard | Weekly safe-to-spend once; one goal progress bar; saved/target amounts, date and weeks remaining; one pace badge; relevant shortfall or at-risk warning; up to four dated plan inputs; links to edit the goal, edit inputs, and calculation details. |
| Calculation | Backend output ledger, goal facts, input counts, calculation date and expandable included income/expenses. No generic next-step panel. |
| Import | CSV template, file picker, preview, row errors, explicit replacement warning, confirm/cancel. |

Dashboard setup shows one next action: create the missing goal, add the cash
balance, or confirm the reserve. It must not show a spending amount before the
backend marks the plan ready. Errors and loading remain explicit.

Latest changes are expandable and appear only when input categories changed or
the backend reports a nonzero allowance change. Unconfirmed income is shown as
an actionable warning only when its count is positive. The income/expense list
shows saved dates, not computed recurrence or claims that dates are in the future.

The optional AI digest is visible directly below weekly safe-to-spend and above
goal progress. It has an explicit Generate digest action; generation is not
automatic. The expanded result shows an overview, distinct observations with
trusted evidence values, and a suggested review action linked to goal or input
editing. The richer content and its bounds are defined by SPEC-0011. Failure
offers retry, disabled availability hides the panel, and a digest for a different
snapshot is never paired with the current dashboard's values.

## Data and calculation boundary

The dashboard uses `DashboardItem.goal`, `DashboardItem.pace`, `calculated_at`,
`explanation.summary.unconfirmed_income_count`, and `changed_from_previous`.
Saved input rows come from the latest snapshot's normalized income and expenses.
The calculation ledger formats `result_json.outputs` values: current cash,
confirmed future income, planned future expenses, reserve, forecast resources,
goal gap, discretionary capacity, remaining weeks, and weekly safe-to-spend.
The frontend does not derive these amounts or calculate a new savings-pace gap.

Income and expense forms start expanded for empty lists. Once entries exist,
the saved entries come first and add forms are collapsed. Editing an entry opens
its form. Archiving is available in a separate disclosure below goal saving.

No new entities, financial metrics, API endpoints, or deferred capabilities are
introduced. Backend ownership and snapshot immutability are unchanged.

## Visual verification contract

`frontend/scripts/ui-fixture.json` contains fixed responses captured from the
local backend after importing the repository's synthetic planning CSV template.
The account email and CSRF token are synthetic placeholders. The fixture uses
real API response fields and backend-calculated financial outputs. It is test
data only, never a fallback in the production application.

`frontend/scripts/capture-dashboard.mjs` intercepts API requests with that fixture
and renders the actual application at 1600×1000, 1024×768, and 390×844. It captures
all eight routes plus a generated digest state, checks page errors and horizontal overflow, and writes
transient PNGs to `/tmp/goal-wise-ui` by default. Unauthenticated captures use a
401 session response. The digest uses an accepted provider response for the
same synthetic metrics from `frontend/scripts/ai-digest-at-risk-fixture.json`;
the capture clicks Generate digest and renders its full response and review link.
UI end-to-end tests separately verify real mutations,
missing setup, AI success/failure, and ownership isolation against a local API.

## Verification

- Frontend lint, unit tests, and production build.
- End-to-end setup, login/logout, goal lifecycle, dashboard status, CSV preview
  and confirmation, and explicitly requested AI explanation.
- Browser inspection of all routes at desktop, tablet, and mobile sizes.
- No lost labels, hidden primary actions, duplicated progress indicators, or
  unconditional explanatory panels.
