# User Story: Elena Revises a Medical Goal Midway Through the Plan

## Persona

Elena is halfway through saving for a medical deductible. Her insurer sends a
new estimate that raises the likely out-of-pocket payment from `$1,800` to
`$2,400`. She asks an AI assistant to draft an updated GoalWise planning CSV
using the supplied template, then reviews the draft before replacing her plan.

## Story

As a household planner whose assumptions changed, Elena wants to replace her
current goal and financial inputs in one reviewed import so her weekly spending
number reflects the new deadline and cost.

## What changed

Elena's original plan was the [healthcare deductible story](healthcare-deductible.md).
The updated draft changes:

- the target from `$1,800` to `$2,400`;
- current saved money to `$1,300`, representing progress halfway through the
  revised plan;
- the deductible payment from `$600` to `$1,100`;
- the reserve buffer from `$300` to `$500`;
- the annual bonus remains explicitly `unconfirmed`.

The complete draft is [elena-medical-deductible-revised.csv](../../frontend/public/elena-medical-deductible-revised.csv).
It is a replacement document: importing it replaces Elena's current goal,
cash profile, income sources, and planned expenses after confirmation.

## Demo flow

1. Sign in as `elena.deductible@example.com` with the local demo password.
2. Record the current dashboard status, weekly allowance, and shortfall.
3. Open the planning import flow and select
   `elena-medical-deductible-revised.csv`.
4. Explain that an AI assistant produced a draft from the GoalWise template;
   Elena still owns the assumptions and must review every normalized value.
5. Show the preview: the revised target, current saved amount, reserve, income
   confidence, and two planned expenses.
6. Cancel once to demonstrate that the existing goal and snapshot remain
   unchanged.
7. Upload the file again and explicitly confirm the replacement.
8. Reopen the dashboard and calculation details. The backend recalculates the
   result and creates a new immutable snapshot.
9. If desired, request an explain-only digest and show that it describes the
   new snapshot without changing its values.

## Acceptance criteria

- The CSV passes the canonical header, row, amount, date, recurrence, and
  singleton `goal`/`cash` rules.
- Preview clearly identifies the import as a full replacement before any data
  is changed.
- Cancel leaves Elena's prior goal, inputs, and latest snapshot intact.
- Confirmation atomically replaces the setup or leaves the prior setup intact
  if persistence fails.
- The imported bonus remains unconfirmed and is excluded from confirmed future
  income by `pace-v1`.
- The revised official result is calculated by the backend; the CSV supplies no
  safe-to-spend amount, pace status, or snapshot.
- The prior immutable snapshot remains auditable after replacement.

## AI and product boundary

The AI assistant may format Elena's stated assumptions into the canonical CSV
template or explain a committed snapshot. It must not invent amounts, classify
expenses, calculate pace, or override GoalWise results. Elena reviews the draft,
and the authenticated import preview plus explicit confirmation are the source
of truth.

This story demonstrates a realistic assumption change while staying within the
single-goal, manual-input MVP. It does not imply bank synchronization, raw
transaction import, medical advice, or automatic AI updates.
