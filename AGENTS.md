# Agent Guidelines

These instructions apply to coding agents working in this repository.

## Start Here

Before making changes, read:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [DESIGN.md](DESIGN.md)

For architecture or behavior changes, also consult:

- [ADRs](docs/adr/README.md)
- [Implementation specs](docs/specs/README.md)
- [SRS](docs/srs/goal-wise-srs-v1.md)
- [MVP scope mapping](docs/specs/0007-srs-traceability-and-mvp-scope.md)

## Architectural Discipline

GoalWise is a progressive MVP/PDR subset of the broader SRS. Do not silently expand scope.

Current MVP priorities:

- One active savings goal.
- Manual financial assumptions.
- Deterministic `pace-v1` calculation.
- Immutable calculation snapshots.
- Backend-owned dashboard values.
- User-owned data isolation.
- AI-free financial core.

Deferred areas include CSV import, AI summaries, export/delete, background scheduling, and multi-goal support. Do not implement deferred areas unless the user explicitly asks and the scope docs are updated.

## Drift Warnings

Warn the user before making a change that drifts from existing architecture decisions or specs.

Examples of drift:

- Moving safe-to-spend calculation into the frontend.
- Letting AI calculate or override financial outputs.
- Storing money as floating-point values.
- Returning `403` for cross-user private resource access instead of `404`.
- Mutating calculation snapshots after insert.
- Adding CSV, AI, export/delete, scheduler, or multi-goal behavior without updating scope docs.
- Changing auth/session/CSRF behavior without updating the auth spec.

When drift is intentional, update the relevant ADR, spec, and plan in the same change.

## Documentation Updates

If a change affects architecture, behavior, security, API contracts, data shape, deployment, or MVP scope:

- Update the relevant spec in `docs/specs/`.
- Add or update an ADR in `docs/adr/` when the "why" changes.
- Update `DESIGN.md` when backend/data/API/calculation design changes.
- Update `ARCHITECTURE.md` only for high-level system changes.
- Update the MVP scope mapping when SRS implementation status changes.

ADRs explain why. Specs define exactly how.

## Implementation Boundaries

- The backend is the source of truth for financial calculations and official dashboard metrics.
- The React frontend may format and visualize backend values, but must not duplicate pace-engine formulas.
- The pace engine must remain deterministic and independent of FastAPI, SQLAlchemy, sessions, frontend code, and AI providers.
- Store money as integer cents.
- Store timestamps in UTC and date-only values in the user's local calendar semantics.
- Use server-side ownership checks for every protected user-owned resource.
- Keep raw transaction descriptions out of immutable calculation snapshots.

## Git Workflow

Follow [CONTRIBUTING.md](CONTRIBUTING.md):

- Branch from `development`.
- Rebase on latest `development`; do not merge `development` into feature branches.
- Open PRs back into `development` unless instructed otherwise.
- Do not merge your own PR.
- Use consistent commit descriptors such as `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, and `chore:`.

## Verification

Run relevant checks before finishing a change. If tests or checks are not available yet, state what was reviewed manually.

For docs-only changes:

- Check links and indexes.
- Check Mermaid diagrams render when changed.
- Check for stale or contradictory wording.

For implementation changes:

- Add or update tests that match the risk of the change.
- Prioritize pace-engine golden tests for calculation behavior.
- Include cross-user access tests for protected resources.
- Include auth/session/CSRF tests for authentication changes.

