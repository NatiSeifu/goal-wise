# Phase 9 - Goal Lifecycle and Product UI Polish

## Purpose

Close the gap between the backend-supported GoalWise MVP concepts and the
visible product UI.

The immediate driver is goal lifecycle support. The SRS and specs require that a
user with an active goal can edit, complete, or archive it. The current data
model already has `Goal.status` and `archived_at`, and the backend already marks
a goal `completed` when current saved reaches the target. However, there is no
explicit archive endpoint and no user-facing archive action.

This phase also captures nearby product UI issues found while validating the user
stories:

- implementation/audit terms such as snapshot IDs should be translated into
  user-facing calculation history;
- dashboard "changed from previous" categories should be human readable;
- supported backend actions should be visible in the UI;
- UI actions must not imply hard deletion when the backend preserves history.

## Source of Truth

- `docs/srs/goal-wise-srs-v1.md`
- `docs/specs/0003-pace-engine-behavior.md`
- `docs/specs/0007-srs-traceability-and-mvp-scope.md`
- `docs/PRODUCT_CONTEXT.md`
- `DESIGN.md`
- backend goal model/service/repository/API code
- frontend goal/dashboard/calculation routes

## Current Baseline

Already present:

- `Goal.status` supports `active`, `completed`, and `archived`.
- `Goal.archived_at` exists in the database model and response schema.
- one active goal per user is enforced through a partial unique index.
- `GET /api/v1/goals/active` excludes completed and archived goals.
- goal update marks the goal `completed` when current saved reaches target.
- snapshots preserve goal status in normalized input JSON.

Missing:

- explicit archive service behavior;
- explicit archive API endpoint;
- frontend archive action;
- user-facing explanation of what archive means;
- tests for archive behavior and cross-user access;
- humanized dashboard/category labels for calculation history.

## Scope

In scope:

- archive active goal through a CSRF-protected API endpoint;
- preserve goal history and snapshots when archiving;
- set `archived_at` for archived goals;
- ensure archived goals are not returned as active;
- allow creating a new active goal after archiving the previous active goal;
- frontend archive action with clear copy and pending/error states;
- humanized calculation history labels for changed input categories.

Out of scope:

- hard-deleting goals;
- listing archived goal history;
- restoring archived goals;
- multiple active goals;
- account export/delete;
- transaction history;
- AI explanations.

## Architecture Decisions

### Archive, not delete

Use archive semantics for this MVP. Archiving removes the goal from active
planning while preserving immutable calculation history. This aligns with the
SRS data-retention model and snapshot auditability.

Hard delete is not recommended because:

- snapshots reference goals;
- user trust depends on preserving why prior dashboard values existed;
- deletion/export workflows are deferred data-rights work.

### Endpoint shape

Recommended endpoint:

```text
POST /api/v1/goals/{goal_id}/archive
```

Rationale:

- archive is an action on a goal resource;
- it is CSRF-protected and state-changing;
- it preserves the goal record, so `DELETE /goals/{goal_id}` would be
  misleading.

## Slice 1 - Backend Archive Behavior

Build:

- repository helper to archive a goal;
- service function `archive_goal_for_user`;
- route `POST /api/v1/goals/{goal_id}/archive`;
- no new pace snapshot on archive; the archived goal remains persisted and prior
  immutable snapshots remain the calculation history.

Success criteria:

- authenticated owner can archive an active goal;
- `archived_at` is set;
- archived goal status is `archived`;
- `GET /api/v1/goals/active` returns `item: null` after archive;
- cross-user archive returns `404`;
- CSRF is required;
- user can create a new active goal after archiving the previous one.

## Slice 2 - Frontend Goal Archive Action

Build:

- archive API resource function;
- archive action on the goal route when an active goal exists;
- clear confirmation-free copy that does not say "delete";
- pending/error/success state;
- form reset after archive.

Success criteria:

- user can archive the active goal from the frontend;
- archived goal disappears from active goal form state;
- user can create a new goal afterward;
- UI states do not imply hard deletion or data export/deletion support.

## Slice 3 - Calculation History Language

Build:

- map `changed_input_categories` to human labels:
  - `goal` -> `Goal details`
  - `financial_profile` -> `Financial profile`
  - `income_sources` -> `Income sources`
  - `planned_expenses` -> `Planned expenses`
  - `transactions` -> `Transactions`
- rename visible "Snapshot trail" style text to calculation-history language
  where appropriate.

Success criteria:

- dashboard no longer shows underscore keys such as `planned_expenses`;
- snapshot IDs remain available only where useful for audit/debug context;
- normal users see "latest calculation" or "calculation history" language.

## Slice 4 - UI Polish Audit From Story Users

Audit the seeded users:

- Maya: `At Risk`
- Jordan: `On Track`
- Sam: `Off Pace`

Fix only concrete issues:

- unclear status hierarchy;
- confusing calculation explanation;
- awkward dashboard-to-edit navigation;
- unsupported or overly technical copy.

Success criteria:

- each story dashboard communicates its state without requiring developer
  explanation;
- frontend still renders backend-owned values only;
- no deferred capabilities appear as current behavior.

## Suggested Commit Slices

1. `docs: plan goal lifecycle ui polish`
2. `feat: add goal archive backend behavior`
3. `feat: add goal archive frontend action`
4. `fix: humanize calculation history labels`
5. `fix: polish story dashboard copy`

## Phase Completion Criteria

- Goal archive behavior is available through backend API and frontend UI.
- Archived goals preserve history and no longer count as active.
- Users can create a new active goal after archiving.
- Dashboard and calculation language is user-facing rather than raw backend
  implementation language.
- Backend and frontend checks pass.
