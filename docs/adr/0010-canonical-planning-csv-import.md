# ADR-0010: Use a Canonical Planning CSV for Structured Imports

- **Status:** Accepted
- **Date:** 2026-08-27
- **Deciders:** Nati Seifu
- **Related requirements:** FR-INP-008, FR-GOAL-001 to FR-GOAL-004, FR-FIN-001 to FR-FIN-007, FR-ERR-001, NFR-SEC-006, NFR-SEC-008, NFR-PRI-001, NFR-REL-001

## Context

GoalWise currently accepts manual planning assumptions: one active savings
goal, a financial profile, expected income sources, and planned expenses. The
broader SRS also describes transaction import, but a bank statement and a
GoalWise planning assumption are not the same thing. A bank transaction says
what happened; a planned income or expense says what the user expects to
happen before the goal date.

The next increment needs an import format that can be produced by a person or
by a separate converter without requiring GoalWise to guess financial meaning.
The course MVP remains a progressive subset, and ADR-0007 deferred CSV import
from the original manual-only increment. This ADR defines the accepted
canonical planning import extension; raw transaction import remains deferred.

The design must preserve the existing architectural drivers:

- deterministic financial calculations;
- the backend as the source of truth;
- integer-cent money storage;
- date-only local-calendar semantics;
- user-owned data isolation;
- immutable snapshots;
- understandable validation and review before persistence.

## Decision

We will define one canonical, row-oriented CSV format for importing a
complete GoalWise planning setup. The format will contain `goal`, `cash`,
`income`, and `expense` rows, with `record_type` selecting the row contract.

The importer will map rows to existing GoalWise domain concepts, normalize
decimal dollar amounts to integer cents, validate dates and enumerations, and
run the existing deterministic calculation path after explicit confirmation.
It will not import raw bank statements, infer planning meaning, accept
client-provided results, or call an AI provider at runtime.

The exact contract is defined by [SPEC-0010](../specs/0010-planning-csv-import.md).

## Alternatives considered

- **Treat bank statements as the import contract** - Rejected because raw
  transaction history does not directly express future income, planned
  expenses, reserve policy, or goal state. It would force GoalWise to infer
  financial meaning and create correction and duplicate workflows before the
  core planning import is useful.
- **Import only income and expenses** - Rejected because the resulting file
  could not recreate a complete planning setup; users would still need to
  enter the goal and cash position manually.
- **Use separate files for goals, cash, income, and expenses** - Rejected for
  the first increment because it increases user and converter coordination
  cost and makes an all-or-nothing preview harder to understand.
- **Accept a flexible column set and infer missing values** - Rejected because
  silent inference would make imports difficult to audit and could alter
  financial guidance without an explicit user decision.
- **Let the CSV include safe-to-spend or pace results** - Rejected because
  official financial outputs must be calculated by the backend's deterministic
  `pace-v1` engine.

## Consequences

**Positive:**

- A converter outside GoalWise has a stable target contract.
- The import maps directly to existing form-backed domain models.
- The backend retains ownership of validation, calculations, snapshots, and
  user isolation.
- The format is sufficient to recreate a complete planning setup.
- Raw transaction descriptions and bank credentials stay outside this feature.

**Negative:**

- Users or external tools must translate other formats into the canonical CSV.
- The format is stricter than a general-purpose bank statement importer.
- A later transaction-history feature will need a separate contract and must
  not be conflated with this planning import.

**Neutral / follow-ups:**

- The implementation is a progressive increment beyond the original
  manual-only subset while the broader SRS mapping remains in force.
- A future transaction import may reuse parser and upload-safety utilities,
  but it needs its own data model, semantics, and scope decision.
- Replacing or merging an existing setup is recorded separately in ADR-0011.

## AI assistance & provenance

AI helped compare raw bank-statement import with structured planning-input
import, enumerate alternatives, and draft the contract. The project owner
decided that the converter is outside GoalWise and that the application should
accept only a canonical format. The decision was checked against the SRS v2.0
manual-input boundary, ADR-0002's deterministic-core decision, ADR-0007's
deferral, and SPEC-0010. No runtime AI behavior is introduced by this ADR.
