# GoalWise

GoalWise is a goal-oriented budgeting app that helps a user understand whether they are on pace to reach one near-term savings goal. Instead of focusing on broad category budgeting, the product turns a savings target, current cash, expected income, planned expenses, and a reserve buffer into a weekly safe-to-spend number.

The current repository captures the architecture and planning package for the MVP/PDR stage. It is a progressive subset of the broader SRS, focused on proving the core planning loop before adding imports, AI summaries, export/delete workflows, and deeper automation.

## Core Idea

GoalWise is built around a deterministic financial core:

- Users enter a goal and manual financial assumptions.
- The backend validates the data and enforces ownership.
- A deterministic pace engine calculates safe-to-spend, shortfall, and pace status.
- Each calculation is stored as an immutable snapshot so the result can be explained and audited.

AI may be added later for summaries or transaction classification, but it does not calculate or override the safe-to-spend amount.

## Architecture

The MVP architecture uses:

- React + Vite for the frontend.
- FastAPI for the backend API.
- SQLAlchemy and Alembic for persistence.
- PostgreSQL for hosted deployment, with SQLite allowed for local development and tests.
- A deterministic `pace-v1` calculation engine.
- Immutable calculation snapshots for explanation and traceability.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the high-level system view and [DESIGN.md](DESIGN.md) for backend design details.

## Backend Runtime

Backend tooling uses `uv` with the project environment at `.venv`.

Common backend commands:

```text
make backend-sync
make backend-check
make backend-db-up
make backend-stack-up
make backend-migrate
make backend-migration-current
```

`make backend-migrate` applies Alembic migrations to the configured `DATABASE_URL`. Local development may use SQLite; deploy-readiness work should also verify migrations against PostgreSQL before hosted demo use.

The local PostgreSQL Compose workflow is documented in [backend/README.md](backend/README.md).
Backend CI runs on pull requests to `development` for backend-related changes.

## Documentation

Key project documents:

- [SRS](docs/srs/goal-wise-srs-v1.md)
- [Architecture overview](ARCHITECTURE.md)
- [Backend design](DESIGN.md)
- [Product context](docs/PRODUCT_CONTEXT.md)
- [Contributing guidelines](CONTRIBUTING.md)
- [Architecture decision process](docs/architecture-decision-process.md)
- [ADRs](docs/adr/README.md)
- [Implementation specs](docs/specs/README.md)
- [MVP scope plan](.agents/plans/00-mvp-scope.md)

Slide assets for the technical architecture presentation are in [docs/slides](docs/slides).

## MVP Scope

Included in the current MVP architecture:

- Account access and user-owned data isolation.
- One active savings goal.
- Manual income and planned-expense inputs.
- Deterministic weekly safe-to-spend calculation.
- Pace status and shortfall calculation.
- Immutable calculation history.
- Dashboard-ready result and explanation data.

Deferred until later increments:

- CSV import and transaction correction.
- AI-generated summaries.
- Account export and deletion.
- Background scheduling.
- Multi-goal support.
