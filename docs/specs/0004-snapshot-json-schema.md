# SPEC-0004: Snapshot JSON Schema

Status: Accepted
Last Updated: 2026-08-01
Related ADRs: ADR-0002, ADR-0003, ADR-0004
Source Requirements: FR-PACE-005, FR-PACE-006, FR-UI-002, NFR-PRI-002

## Purpose

Define the versioned JSON shapes stored in `CalculationSnapshot.normalized_input_json` and `CalculationSnapshot.result_json`.

Snapshots must be sufficient to audit and reproduce a calculation without reading mutable current records. They must also avoid copying unnecessary sensitive text into immutable history.

## Database Columns

The database stores snapshot data in two JSON columns:

```text
normalized_input_json json
result_json json
```

The schema is enforced by application validation and tests.

## Input Schema

`normalized_input_json` uses `schema_version = "snapshot-input-v1"` for the MVP.

```json
{
  "schema_version": "snapshot-input-v1",
  "formula_version": "pace-v1",
  "calculation": {
    "timestamp_utc": "2026-08-01T17:00:00Z",
    "user_time_zone": "America/Los_Angeles",
    "trigger": "goal_updated"
  },
  "goal": {
    "id": "goal_123",
    "name": "Emergency fund",
    "target_cents": 300000,
    "initial_saved_cents": 50000,
    "current_saved_cents": 75000,
    "start_date": "2026-08-01",
    "target_date": "2026-12-31",
    "status": "active"
  },
  "financial_profile": {
    "starting_cash_cents": 120000,
    "balance_as_of_date": "2026-08-01",
    "reserve_buffer_cents": 5000,
    "reserve_buffer_confirmed": true
  },
  "income_sources": [
    {
      "id": "inc_123",
      "name": "Campus job",
      "amount_cents": 45000,
      "next_date": "2026-08-07",
      "frequency": "weekly",
      "confidence": "confirmed",
      "active": true
    }
  ],
  "planned_expenses": [
    {
      "id": "exp_123",
      "name": "Rent",
      "amount_cents": 90000,
      "next_date": "2026-09-01",
      "frequency": "monthly",
      "classification": "essential",
      "active": true
    }
  ],
  "transactions": []
}
```

## Result Schema

`result_json` uses `schema_version = "snapshot-result-v1"` for the MVP.

```json
{
  "schema_version": "snapshot-result-v1",
  "formula_version": "pace-v1",
  "outputs": {
    "current_cash_cents": 120000,
    "confirmed_future_income_cents": 900000,
    "planned_future_expenses_cents": 450000,
    "reserve_buffer_cents": 5000,
    "forecast_resources_cents": 565000,
    "goal_gap_cents": 225000,
    "discretionary_capacity_cents": 340000,
    "remaining_weeks": 22,
    "weekly_safe_to_spend_cents": 15400,
    "projected_shortfall_cents": 0,
    "expected_savings_to_date_cents": 75000,
    "pace_status": "On Track",
    "progress_percentage": 25.0,
    "current_week_opening_allowance_cents": 15400,
    "current_week_remainder_cents": 15400
  },
  "explanation": {
    "included_income_source_ids": ["inc_123"],
    "excluded_income_source_ids": [],
    "included_planned_expense_ids": ["exp_123"],
    "excluded_planned_expense_ids": [],
    "summary": {
      "confirmed_income_count": 1,
      "planned_expense_count": 1,
      "unconfirmed_income_count": 0
    }
  },
  "changed_from_previous": {
    "previous_snapshot_id": null,
    "changed_input_categories": [],
    "weekly_safe_to_spend_delta_cents": null
  }
}
```

## User-Authored Labels

Snapshot inputs may include short user-authored planning labels:

- Goal name.
- Income source name.
- Planned expense name.

These labels make dashboard explanations and review/debugging understandable without joining back to mutable records.

## Transaction Minimization

When transaction support is implemented, detailed transaction records remain in the user-owned `Transaction` table. Immutable snapshots must not copy raw transaction descriptions.

Allowed transaction facts in snapshots:

```json
{
  "id": "txn_123",
  "date": "2026-08-03",
  "amount_cents": -1850,
  "category": "discretionary_spending",
  "source": "csv",
  "duplicate_status": "accepted",
  "included_in_current_cash": true
}
```

Disallowed transaction fields in snapshots:

```json
{
  "description": "VENMO JOHN DOE DINNER",
  "raw_description": "VENMO JOHN DOE DINNER",
  "normalized_description": "venmo john doe dinner",
  "original_values": {}
}
```

Rationale:

- Transaction descriptions may contain merchant names, employers, medical providers, person names, locations, or account fragments.
- Snapshots are immutable and can duplicate one transaction across many recalculations.
- Calculation auditability needs transaction date, amount, category, source, duplicate status, and inclusion decision, not raw description text.
- Transaction insights and correction workflows should query the `Transaction` table.

## Versioning Rules

- `schema_version` is required in both JSON columns.
- `formula_version` is required in both JSON columns.
- Incompatible shape changes require a new schema version.
- Incompatible formula changes require a new formula version.
- Old snapshots must remain readable after schema or formula changes.

## Verification

Required tests:

- Snapshot input JSON includes `schema_version`, `formula_version`, `calculation`, `goal`, `financial_profile`, `income_sources`, `planned_expenses`, and `transactions`.
- Snapshot result JSON includes `schema_version`, `formula_version`, `outputs`, `explanation`, and `changed_from_previous`.
- Snapshot outputs include every field required by SPEC-0003.
- Snapshot or dashboard API responses include official progress percentage and current-week remainder when shown by the dashboard.
- Snapshot input JSON includes goal, income source, and planned expense names when present.
- Snapshot transaction entries reject raw description fields.
- Latest two snapshots can be compared by `changed_input_categories` and `weekly_safe_to_spend_delta_cents`.
- Old snapshots are not modified when current goal, income, expense, or transaction rows change.
