# Phase 14 - Typed Snapshot Contracts

## Objective

Make calculation snapshots first-class typed application contracts. A snapshot
is not typed only for the AI explanation feature: it is the historical record
of the deterministic calculation and must be validated like every other
important application data shape.

The database may continue storing snapshot documents in JSON columns. The
application must validate those documents through explicit versioned models
when they cross the persistence boundary.

Source contracts:

- [SPEC-0004: Snapshot JSON Schema](../../docs/specs/0004-snapshot-json-schema.md)
- [ADR-0003: Use Immutable Calculation Snapshots](../../docs/adr/0003-immutable-calculation-snapshots.md)
- [SPEC-0011: Bounded AI Explanation Layer](../../docs/specs/0011-ai-explanation-layer.md)

## Problem to correct

`CalculationSnapshot.normalized_input_json` and `result_json` are currently
typed as broad dictionaries. This makes the JSON column convenient, but it
pushes shape checking into scattered consumers and requires defensive checks
such as `isinstance` before reading known fields.

This is a typing boundary problem, not an AI problem. AI is only the first
consumer that exposed it clearly.

## Design

Add application-owned, versioned Pydantic contracts for both snapshot
documents:

- `SnapshotInputV1` for `normalized_input_json`;
- `SnapshotResultV1` for `result_json`;
- nested contracts for calculation metadata, goal/profile/input facts,
  deterministic outputs, explanation metadata, and change-from-previous data.

The contracts should use integer types for all money values, a bounded numeric
type for percentages, explicit strings/enums for formula and status values, and
nullable fields where the snapshot schema permits `null`.

The JSON database columns remain JSON because snapshots are immutable historical
documents. Pydantic models provide application validation and typed access; ORM
models continue to represent persistence entities and relationships.

## Implementation slices

### Slice 1 - Model the versioned contracts

Create the typed input and result models without changing runtime behavior.
Match the exact shapes already defined in SPEC-0004 and the output produced by
`snapshot_json.py`. Decide explicitly which fields are required, nullable, or
allowed to evolve.

Success criteria:

- Valid existing snapshot fixtures validate successfully.
- Invalid schema versions, missing required fields, wrong money types, and
  malformed nested objects fail with a typed contract error.
- No calculation formula or API behavior changes.

### Slice 2 - Validate at snapshot creation

Make snapshot creation accept typed contracts or validate incoming dictionaries
immediately before persistence. Serialize the validated models to JSON for the
SQLAlchemy column.

Success criteria:

- No invalid snapshot document can be inserted through the application
  repository/service path.
- Snapshot immutability remains unchanged.
- Existing calculation, import, and migration workflows continue to pass.

### Slice 3 - Validate at snapshot read boundaries

Add a single conversion boundary for persisted JSON, such as
`parse_snapshot_input()` and `parse_snapshot_result()`. Use it in repositories
or services that consume snapshot documents.

Success criteria:

- Consumers receive typed contracts instead of arbitrary nested dictionaries.
- A malformed historical record fails in one documented way rather than with
  scattered `KeyError`, `TypeError`, or `AttributeError` behavior.
- Versioned compatibility behavior is explicit for old snapshots.

### Slice 4 - Migrate consumers

Update dashboard, weekly-plan, snapshot comparison, AI payload construction,
and any future export/reporting code to use the typed contracts.

Success criteria:

- No consumer manually traverses known snapshot fields through untyped JSON.
- Official dashboard values still come only from the deterministic snapshot.
- AI payload construction remains allowlisted and cannot access unrelated
  snapshot data accidentally.

### Slice 5 - Remove obsolete defensive checks

After consumers use the validated contracts, remove `isinstance` checks that
exist only because snapshot JSON is currently untyped. Retain checks at true
untrusted boundaries, such as raw database JSON before parsing and provider
responses before validation.

Success criteria:

- Defensive checks are removed only where typed parsing now guarantees the
  shape.
- Boundary validation remains in place.
- Tests cover malformed persisted JSON and prove failures are controlled.

### Slice 6 - Compatibility and regression verification

Test current fixtures, historical version behavior, SQLite, PostgreSQL
migrations, dashboard reads, snapshot comparisons, and AI explanation reads.
Document how a future `snapshot-result-v2` is introduced without rewriting old
snapshots.

Success criteria:

- Existing snapshots remain readable.
- New schema versions cannot silently be interpreted as old versions.
- Full backend checks pass with no changes to financial calculations.

## Explicit non-goals

- Do not normalize snapshot JSON into many relational tables.
- Do not make AI-specific models the source of snapshot typing.
- Do not move deterministic calculations into Pydantic validators.
- Do not alter the immutable snapshot lifecycle.
- Do not discard or rewrite historical snapshots during migration.

## Verification checklist

- [ ] SPEC-0004 shape is represented by typed application contracts.
- [x] Input and result documents are validated before persistence.
- [x] Persisted documents are parsed through one typed boundary.
- [x] Dashboard and weekly-plan consumers use typed values.
- [x] AI payload extraction uses the typed result contract and its allowlist.
- [x] Obsolete `isinstance` checks are removed only after migration.
- [ ] Malformed and unknown-version snapshots fail predictably.
- [ ] SQLite and PostgreSQL compatibility remains intact.
- [ ] Full backend tests, Ruff, and mypy pass.
