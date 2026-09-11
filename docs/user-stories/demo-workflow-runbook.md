# User Story: Recoverable Planning Import and Explainable Review

This runbook is a production-style demo companion for the financial stories. It
shows how a user can bring a complete plan into GoalWise, review it before
replacement, and request an explanation without giving AI authority over money.

## Story A: Priya imports a complete relocation plan

### Context

Priya has already prepared one structured planning file for a relocation. She
wants to avoid retyping the goal, cash, income, expenses, and reserve. She needs
to know exactly what will be replaced before committing it.

### Demo flow

1. Sign in as Priya.
2. Open the planning import screen and download the canonical template.
3. Upload a complete file containing one goal, financial profile, income rows,
   and planned-expense rows.
4. Review normalized values and any row-level errors in the preview.
5. Show the explicit replacement warning: confirmation replaces the current
   planning setup for this user.
6. Cancel once and verify the previous goal and snapshot remain unchanged.
7. Upload the same valid file again and confirm it.
8. Open the dashboard and calculation details to show the new backend-owned
   result and a new immutable snapshot.

### What this proves

- Import is a previewed, explicit, atomic replacement workflow.
- The user can recover from cancellation without losing the last valid plan.
- Imported values still pass through the same deterministic pace engine as manual
  inputs.
- Raw CSV content is not copied into immutable calculation snapshots.

### Acceptance criteria

- A malformed or incomplete file stays in preview with actionable row errors.
- Cancel leaves the prior plan and latest snapshot intact.
- Confirm replaces the complete setup atomically or leaves the prior setup intact
  if persistence fails.
- A preview from another authenticated user cannot be read or confirmed.
- The dashboard result after confirmation is calculated by the backend.

### MVP boundaries

- This is a canonical planning CSV, not a bank-statement or transaction import.
- The file does not classify transactions, detect duplicates, or connect a bank.

## Story B: A reviewer requests an explain-only digest

### Context

After Priya confirms the plan, a reviewer wants a plain-language explanation of
the committed snapshot. The explanation should help the reviewer understand the
inputs and the result while leaving the financial output authoritative.

### Demo flow

1. On the dashboard, record the displayed weekly safe-to-spend, pace status, and
   shortfall before requesting any explanation.
2. Click the explicit Generate digest action.
3. Show that the request is scoped to the authenticated user's latest committed
   snapshot and uses minimized aggregate facts.
4. Display the returned overview, observations, evidence values, and review link.
5. Trigger a provider-disabled or timeout fixture and show the retryable
   unavailable state.
6. Return to the dashboard and verify the authoritative values have not changed.

### What this proves

- AI is an explanation layer, not a calculator or decision maker.
- A provider outage does not block the deterministic financial workflow.
- The digest is tied to the snapshot it explains and cannot be paired with a
  different dashboard result.
- Retry, disabled, malformed-response, and provider-error states are visible.

### Acceptance criteria

- The digest includes only minimized snapshot facts and non-identifying context.
- AI cannot alter safe-to-spend, pace status, shortfall, or snapshot contents.
- A failed provider request produces an explicit unavailable or retryable state.
- A digest for an older snapshot is never presented as the current calculation.
- Sensitive credentials, raw descriptions, and full financial payloads are not
  exposed in the UI or operational logs.

### MVP boundaries

- AI does not classify transactions, generate financial decisions, or provide
  investment, tax, borrowing, or medical advice.
- The explanation is optional and never required to calculate or view the plan.
