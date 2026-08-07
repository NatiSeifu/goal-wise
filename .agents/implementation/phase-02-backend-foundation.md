# Phase 2 - Backend Persistence Foundation

## Purpose

Build the backend database foundation that future auth, goal/input, snapshot, and API work can depend on.

This is an execution plan, not a new implementation contract. The source of truth remains:

- `docs/specs/0001-auth-session-security.md`
- `docs/specs/0002-api-response-conventions.md`
- `docs/specs/0004-snapshot-json-schema.md`
- `docs/specs/0005-date-time-semantics.md`
- `docs/specs/0006-railway-deployment.md`
- `docs/specs/0008-project-structure.md`
- `docs/adr/0001-layered-modular-monolith.md`
- `docs/adr/0005-auth-sessions-and-ownership.md`
- `docs/adr/0009-railway-deployment.md`

## Scope

In scope:

- backend runtime dependencies for FastAPI, SQLAlchemy, Alembic, settings, and password hashing;
- environment-driven backend configuration;
- SQLAlchemy base/session wiring;
- portable database type choices for SQLite local/test and PostgreSQL hosted deployment;
- Alembic migration environment;
- initial auth persistence models for `User` and server-side `Session`;
- focused tests proving metadata, model constraints, session wiring, and migrations are usable.

Out of scope:

- auth routes;
- password hashing behavior beyond dependency/config readiness;
- login/logout/session issuance behavior;
- CSRF behavior;
- goal, financial input, and snapshot services;
- frontend work;
- Railway deployment execution.

## Design Decision

Use SQLAlchemy as the database abstraction boundary. Do not create a separate SQLite/PostgreSQL repository ABC or protocol in this phase.

Rationale:

- SQLAlchemy already abstracts runtime database access across SQLite and PostgreSQL for this MVP.
- Repositories will be the application boundary for query behavior.
- A custom database-driver abstraction would add ceremony before there is a second non-SQL persistence backend.
- Portability should be handled through deliberate type choices and tests.

## Portability Rules

- Use integer cents for money.
- Store enum-like values as strings.
- Use date-only columns for user-local financial dates.
- Use timezone-aware UTC timestamps by convention.
- Prefer portable UUID handling that works on SQLite and PostgreSQL.
- Avoid database-native PostgreSQL enum types for MVP migrations.
- JSON columns are acceptable for snapshot input/result payloads later, but avoid DB-specific JSON query behavior in early repository logic.

## Slice 1 - Add Backend Runtime Dependencies

Build:

- update `backend/pyproject.toml`;
- add runtime dependencies for FastAPI, SQLAlchemy, Alembic, Pydantic settings, Argon2 password hashing, and ASGI serving;
- keep dev dependencies intact.

Expected dependency categories:

- FastAPI app/runtime;
- SQLAlchemy ORM;
- Alembic migrations;
- settings/config management;
- password hashing support for later auth work;
- test database utilities only if needed.

Success criteria:

- dependencies install with `uv venv` and `make backend-sync`;
- `make backend-check` passes;
- no application code imports unavailable packages.

## Slice 2 - Add Configuration Layer

Build:

- `backend/app/core/config.py`;
- typed settings object;
- default local SQLite database URL;
- environment variable names for database URL, session secret, cookie flags, allowed frontend origin, and environment name.

Success criteria:

- config can load defaults for local development;
- config can read `DATABASE_URL` for hosted deployment;
- secrets are not hardcoded;
- tests can override settings without mutating global process state unnecessarily;
- `make backend-check` passes.

## Slice 3 - Add SQLAlchemy Base and Session Wiring

Build:

- `backend/app/db/base.py`;
- `backend/app/db/session.py`;
- SQLAlchemy declarative base;
- engine/session factory helpers;
- transaction/session dependency helper suitable for future FastAPI routes.

Success criteria:

- local SQLite engine can be created from default config;
- tests can create an isolated SQLite database;
- SQLAlchemy metadata contains registered models once imported;
- no service/business logic lives in `db/`;
- `make backend-check` passes.

## Slice 4 - Define Portable Type Conventions

Build:

- reusable UUID column/type strategy if needed;
- timestamp helper/type convention if needed;
- tests documenting how UUIDs and timestamps round-trip on SQLite.

Success criteria:

- UUID primary keys work in SQLite tests and remain PostgreSQL-compatible;
- enum-like fields are plain strings at the DB level;
- timestamp fields use UTC-aware values by convention;
- no model uses SQLite-only schema behavior;
- `make backend-check` passes.

## Slice 5 - Add Initial Auth Persistence Models

Build:

- `backend/app/models/user.py`;
- `backend/app/models/session.py`;
- import model metadata through `backend/app/models/__init__.py`.

User model fields:

- `id`;
- normalized unique email;
- password hash;
- time zone;
- created timestamp;
- updated timestamp.

Session model fields:

- `id`;
- `user_id`;
- session token hash;
- CSRF token hash or CSRF token storage strategy to be finalized during auth behavior;
- issued timestamp;
- last seen timestamp;
- expires timestamp;
- revoked timestamp or active/revoked marker.

Success criteria:

- user email has a uniqueness constraint/index;
- session token hash has a uniqueness constraint/index;
- session rows belong to users;
- raw session tokens are not modeled as stored fields;
- model tests prove tables can be created in SQLite;
- `make backend-check` passes.

## Slice 6 - Configure Alembic

Build:

- `backend/alembic.ini` or equivalent backend-local Alembic config;
- `backend/alembic/env.py`;
- migration versions directory;
- first migration creating `users` and `sessions`.

Success criteria:

- Alembic can discover SQLAlchemy metadata;
- migration runs against local SQLite;
- migration definitions are PostgreSQL-compatible;
- migration does not depend on application secrets;
- `make backend-check` passes.

## Slice 7 - Add Foundation Tests

Build tests that assert:

- settings defaults load;
- test database engine/session can create tables;
- metadata includes user and session tables;
- UUIDs round-trip;
- user uniqueness constraint exists or is enforced;
- session token hash uniqueness exists or is enforced;
- model imports do not import FastAPI route modules.

Success criteria:

- tests are deterministic and use isolated temporary SQLite databases;
- tests do not require PostgreSQL locally;
- tests do not require network access;
- `make backend-check` passes.

## Suggested Commit Breakdown

Preferred sequence:

1. `chore: add backend runtime dependencies`
2. `feat: add backend configuration`
3. `feat: add database session wiring`
4. `feat: add auth persistence models`
5. `chore: configure alembic migrations`
6. `test: cover backend persistence foundation`

Acceptable faster sequence:

- combine slices 2 and 3 if the config/session wiring is small;
- keep Alembic setup separate so migration changes are easy to review.

## Phase Completion Criteria

Phase 2 is complete when:

- backend dependencies are declared and installable;
- backend settings load local defaults and hosted database configuration;
- SQLAlchemy base/session wiring exists and is tested;
- `User` and server-side `Session` persistence models exist;
- initial Alembic migration creates the auth foundation tables;
- SQLite local/test path works;
- schema choices remain PostgreSQL-compatible;
- no auth API behavior is required yet;
- `make backend-check` passes.
