# SPEC-0008: Project Structure

Status: Accepted
Last Updated: 2026-08-01
Related ADRs: ADR-0001, ADR-0006, ADR-0008, ADR-0009

## Purpose

This spec defines the initial repository structure for the GoalWise MVP implementation. The structure must support a React + Vite frontend, a FastAPI backend, a deterministic `pace-v1` calculation engine, SQLAlchemy persistence, and Railway deployment.

The structure is intentionally simple. It separates frontend and backend tooling while preserving the backend layer boundaries defined in ADR-0001.

## Repository Layout

GoalWise will use two top-level application directories:

```text
backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
    repositories/
    pace_engine/
  alembic/
  tests/

frontend/
  src/
    app/
    api/
    components/
    features/
    routes/
    styles/
    utils/
```

Do not create a root-level `src/` directory for application code. This repository contains two deployable applications with different toolchains, so `backend/` and `frontend/` are the application roots.

## Backend Directories

### `backend/app/api/`

FastAPI routers and HTTP dependencies live here.

Responsibilities:

- mount routes under `/api/v1`;
- parse requests through Pydantic schemas;
- call service-layer functions;
- return response schemas;
- stay thin and avoid business logic.

Routers must not contain pace formulas, direct SQLAlchemy query logic, or cross-user ownership rules beyond invoking the appropriate dependencies/services.

### `backend/app/schemas/`

Pydantic request and response schemas live here.

Schemas define what crosses the API boundary:

- request bodies;
- response bodies;
- field validation;
- public response shape returned to the React frontend.

Schemas are not database tables. They may intentionally differ from SQLAlchemy models. For example, a `User` database model stores `password_hash`, but no user response schema may expose it.

### `backend/app/models/`

SQLAlchemy ORM models live here.

Models define persistence:

- table names;
- columns;
- foreign keys;
- indexes;
- relationships;
- database constraints.

Models are database objects, not API contracts. API responses should use schemas rather than returning ORM models directly.

### `backend/app/db/`

Database infrastructure lives here.

Responsibilities:

- SQLAlchemy engine creation;
- session factory;
- database dependency wiring;
- shared model metadata;
- local SQLite and hosted PostgreSQL configuration support.

`db/` answers how the app connects to the database. It should not contain goal, income, expense, snapshot, or auth business workflows.

### `backend/app/repositories/`

Repository modules isolate SQLAlchemy queries.

Responsibilities:

- fetch records by id;
- fetch user-owned records by `user_id`;
- create, update, and delete ORM rows;
- hide query details from services;
- keep database access parameterized through SQLAlchemy.

Examples:

- `get_active_goal_for_user(user_id)`;
- `get_latest_snapshot(user_id, goal_id)`;
- `find_session_by_token_hash(token_hash)`;
- `list_active_income_sources(user_id)`.

Repositories are data-access behavior. They should not run pace calculations or decide full business workflows.

### `backend/app/services/`

Application services implement business workflows.

Responsibilities:

- enforce one active goal;
- enforce authenticated user ownership rules;
- coordinate repositories;
- normalize inputs for the pace engine;
- trigger recalculation after valid changes;
- create immutable calculation snapshots;
- return data for API response schemas.

Services may call repositories and the `pace_engine`. Services should receive the authenticated `user_id` explicitly and must not trust `user_id` values from request bodies.

### `backend/app/pace_engine/`

The deterministic pace calculation engine lives here.

Responsibilities:

- accept normalized calculation inputs;
- calculate `pace-v1` outputs;
- return structured calculation results;
- remain deterministic for identical inputs, timestamp, time zone, and formula version.

The pace engine must not import FastAPI, SQLAlchemy, session/auth modules, frontend code, AI provider code, or repository modules.

### `backend/app/core/`

Cross-cutting backend helpers live here.

Responsibilities may include:

- environment configuration;
- security helpers;
- password hashing;
- session token hashing;
- CSRF helpers;
- error types;
- logging/redaction helpers.

`core/` should stay small. If a helper becomes domain-specific, move it to the relevant service, repository, schema, or model module.

### `backend/alembic/`

Alembic migration files and migration environment configuration live here.

Migrations must remain compatible with Railway PostgreSQL. SQLite may be used for local development and tests, but schema choices should not depend on SQLite-only behavior.

### `backend/tests/`

Backend tests live here.

Test organization should mirror risk:

- `tests/pace_engine/` for pure golden tests;
- `tests/api/` for endpoint behavior;
- `tests/services/` for business workflows;
- `tests/repositories/` for ownership and persistence behavior where useful.

The deterministic pace engine must be testable without a database or FastAPI test client.

## Frontend Directories

### `frontend/src/app/`

Application-level React setup lives here.

Responsibilities:

- router setup;
- provider setup;
- app shell;
- authenticated layout wiring.

### `frontend/src/api/`

Frontend API client code lives here.

Responsibilities:

- call the FastAPI `/api/v1` API;
- include cookies on authenticated requests;
- send `X-CSRF-Token` for unsafe authenticated methods;
- normalize API errors for UI display;
- keep endpoint paths centralized.

Frontend API code must not recalculate official backend financial outputs.

### `frontend/src/routes/`

Route-level page components live here.

Examples:

- sign in;
- register;
- dashboard;
- goal setup;
- income sources;
- planned expenses.

Routes may compose feature components and call frontend API hooks/helpers.

### `frontend/src/features/`

Workflow-specific UI and state live here.

Initial feature areas:

- `auth`;
- `dashboard`;
- `goal`;
- `financial-profile`;
- `income-sources`;
- `planned-expenses`.

Feature code may format backend-provided values for display, but it must not duplicate pace-engine formulas or official dashboard metric formulas.

### `frontend/src/components/`

Shared reusable UI components live here.

Examples:

- buttons;
- form fields;
- validation message components;
- layout primitives;
- loading and empty states.

Components in this directory should be generic enough to reuse across multiple features.

### `frontend/src/styles/`

Global styles, design tokens, and shared CSS live here.

### `frontend/src/utils/`

Small frontend-only utilities live here.

Examples:

- formatting integer cents as U.S. dollars;
- formatting ISO dates for display;
- mapping backend status enums to labels/colors/icons.

Utilities must remain display-only. Official values must come from backend API responses.

## Naming Rules

- Use `backend/` and `frontend/` for the two application roots.
- Use `schemas/` for Pydantic API contracts.
- Use `models/` for SQLAlchemy ORM persistence models.
- Use `db/` for connection/session/migration wiring.
- Use `repositories/` for SQLAlchemy query behavior.
- Use `services/` for business workflows.
- Use `pace_engine/` only for deterministic calculation logic.

## Verification

- Backend routers do not contain pace formulas or raw SQLAlchemy query workflows.
- `pace_engine` imports no FastAPI, SQLAlchemy, auth/session, repository, frontend, or AI modules.
- API responses are defined by Pydantic schemas rather than returned ORM models.
- User-owned repository queries filter by `user_id`.
- Frontend code does not duplicate official pace-engine or dashboard formulas.
- Tests can run the pace engine without a database.
