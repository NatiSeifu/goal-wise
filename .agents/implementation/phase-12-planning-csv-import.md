# Phase 12 - Planning CSV Import

## Purpose

Allow a user to import a complete GoalWise planning setup from one canonical
CSV file. The file represents already-structured planning inputs, not raw bank
transactions. A converter outside GoalWise may produce this format later, but
GoalWise only owns validation, preview, persistence, and recalculation.

## Product outcome

After reviewing an import preview, a user can create or replace their current
planning setup with:

- one active savings goal;
- its initial and current saved amounts;
- one cash position and reserve buffer;
- zero or more expected income sources;
- zero or more planned expenses.

The import must use the same domain rules as the existing forms. It must not
introduce a second calculation path or allow imported values to bypass
ownership, validation, snapshot, or lifecycle rules.

## Scope boundary

Included:

- one canonical planning CSV format;
- UTF-8 CSV parsing and row-level validation;
- preview before persistence;
- atomic replacement of the user's planning inputs after confirmation;
- recalculation through the existing service boundary;
- user-isolation, duplicate-record, and invalid-input tests.

Deferred:

- raw transaction or bank-statement import;
- PDF, OFX, QFX, or bank-specific formats;
- external converter or runtime AI;
- automatic inference of recurring income or expenses;
- merging imported data into an existing setup;
- importing multiple active goals;
- changing pace-v1 formulas.

## Canonical CSV contract

The CSV uses one row per domain record. `record_type` determines which fields
are required. Amounts are written in decimal dollars for human and converter
usability, then parsed and stored as integer cents by the backend.

```csv
record_type,name,target_amount,initial_saved,current_saved,starting_cash,balance_date,reserve_buffer,amount,date,frequency,confidence,classification,start_date,target_date
goal,Moving fund,3000.00,500.00,1125.00,,,,,,,,,2026-08-01,2026-11-15
cash,,,,,2000.00,2026-08-26,300.00,,,,,,
income,Salary,,,,,,,2500.00,2026-09-01,biweekly,confirmed,,
expense,Rent,,,,,,,1400.00,2026-09-01,monthly,,essential,,
```

Record rules:

- exactly one `goal` row;
- exactly one `cash` row;
- zero or more `income` rows;
- zero or more `expense` rows;
- unknown record types are invalid;
- required fields depend on the record type;
- dates use `YYYY-MM-DD` and retain the user's local-date semantics;
- `income` and `expense` rows map directly to existing domain models;
- `goal` and `cash` rows map to the existing goal and financial-profile models;
- imported values are subject to the same constraints as form-submitted values.

## Phase 1 - Contract and domain mapping

### Slice 1 - Canonical import contract

Define the header, record types, required fields, amount syntax, date syntax,
blank-field behavior, maximum row count, and file-size limit. Decide whether
the import replaces the current setup or is rejected when an active setup
exists. The initial recommendation is explicit replacement only after a clear
confirmation step.

Success criteria:

- The CSV contract is written in an accepted implementation spec.
- Every CSV field maps to one existing GoalWise domain field.
- The contract states what is rejected and what is not silently inferred.
- SRS scope mapping and relevant ADR/spec indexes are updated if behavior is
  approved for implementation.

### Slice 2 - Domain import object

Create an internal typed representation for a validated import, separate from
SQLAlchemy models and HTTP request schemas. It should contain one goal, one
cash profile, and collections of income and expense inputs.

Success criteria:

- The object is independent of FastAPI, SQLAlchemy, and file-upload details.
- It cannot represent multiple active goals.
- It uses integer cents after parsing.
- Unit tests cover valid complete and minimal plans.

## Phase 2 - Parsing and validation

### Slice 3 - Pure CSV parser

Implement parsing from text or bytes into row records. Handle UTF-8 decoding,
CSV quoting, headers, blank lines, row numbers, and bounded file size without
touching the database.

Success criteria:

- Quoted descriptions and commas are handled by a real CSV parser.
- Malformed files return structured errors with row context.
- Oversized files and excessive row counts are rejected deterministically.
- No partially parsed result is treated as persistable.

### Slice 4 - Row and cross-row validation

Validate amounts, dates, enumerations, required fields, duplicate singleton
rows, and cross-row rules such as exactly one goal and cash row. Reuse domain
validators where practical rather than creating CSV-only business rules.

Success criteria:

- Errors identify row number, field, and user-correctable reason.
- Invalid rows cannot reach repositories.
- Dollar input is converted exactly to cents with no floating-point storage.
- Validation covers past/future date rules and local time-zone semantics.

## Phase 3 - Preview and persistence

### Slice 5 - Preview service and endpoint

Add an authenticated multipart upload endpoint that returns a normalized
preview without changing persisted planning data. The response should include
row counts, normalized values, and row-level errors.

Success criteria:

- Preview requires the authenticated session and CSRF protection.
- The preview contains no data from another user.
- A preview request has no database write side effects.
- The response is bounded and does not echo secrets or uploaded file content
  beyond the fields needed for review.

### Slice 6 - Confirmed atomic import

Add a confirmation operation tied to a validated preview. Persist the complete
planning setup through existing services and repositories in one transaction.
Use the same ownership, active-goal, snapshot, and recalculation behavior as
the existing UI forms.

Success criteria:

- A failed import leaves the prior setup unchanged.
- A successful replacement does not leave stale income or expense rows behind.
- The imported plan produces the same pace result as equivalent form input.
- Calculation snapshots remain immutable and backend-owned.
- Cross-user preview or confirmation attempts return the existing private
  resource contract.

## Phase 4 - Frontend workflow

### Slice 7 - Import and review UI

Add a focused import surface with file selection, validation feedback, a
preview table, explicit confirmation, and success or failure states. Explain
that the file contains GoalWise planning inputs, not a bank statement.

Success criteria:

- Users can understand which rows will create income sources or planned
  expenses and which rows set goal/cash values.
- Invalid rows are actionable without losing the valid preview context.
- Confirmation is visibly distinct from file selection.
- The UI does not duplicate pace formulas or invent unsupported metrics.
- Existing setup forms and dashboard behavior remain intact.

## Phase 5 - Verification and release readiness

### Slice 8 - End-to-end coverage

Add tests for successful complete import, minimal import, malformed CSV,
invalid rows, duplicate singleton rows, replacement behavior, rollback, and
cross-user isolation. Run the flow against the real local PostgreSQL-backed
stack in Playwright and cover parser/service rules with focused unit tests.

Success criteria:

- Preview and confirmation are covered through the browser UI.
- The imported setup is visible in the existing goal, inputs, and dashboard
  views.
- Failed imports do not alter persisted data.
- Existing backend, frontend, and Playwright suites remain green.
- CI uses an isolated database and never staging or production data.

## Accepted Architectural Baseline

The accepted design is a **complete-plan replacement import**: one file
describes one GoalWise setup, preview is required, and confirmation atomically
replaces the current setup. This is simpler and safer than merging arbitrary
rows into existing inputs, while preserving the existing deterministic
calculation boundary. The decision is recorded in ADR-0010 and ADR-0011.

Alternatives retained for future discussion:

- **Import only income and expenses**: simpler CSV, but it cannot recreate a
  complete setup and still requires manual goal and cash entry.
- **Import separate files for each model**: clearer per-file schemas, but more
  cumbersome for users and external converters.
- **Merge imported rows into the current setup**: flexible, but requires
  conflict resolution, duplicate policy, and rollback semantics earlier.

## Completion

Phase 12 is complete: the canonical planning CSV can be previewed,
confirmed, persisted atomically, and verified to produce the same result as
equivalent manual inputs. Raw transaction import remains a separate future
decision.
