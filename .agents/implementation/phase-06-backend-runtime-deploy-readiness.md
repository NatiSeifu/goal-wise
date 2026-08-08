# Phase 6 - Backend Runtime and Deploy Readiness

## Purpose

Make the backend runnable and verifiable in a production-like local environment before the React frontend depends on it.

This phase is about deploy readiness, not deploying to production. The goal is to prove the FastAPI service can start cleanly, connect to PostgreSQL, run migrations, expose health checks, support browser credential flows, and pass CI-style verification.

This is an execution plan, not a new implementation contract. The source of truth remains:

- `CONTRIBUTING.md`
- `README.md`
- `ARCHITECTURE.md`
- `DESIGN.md`
- `docs/specs/0002-api-response-conventions.md`
- `docs/specs/0005-date-time-semantics.md`
- `docs/specs/0008-project-structure.md`
- `docs/adr/0001-layered-modular-monolith.md`
- `docs/adr/0005-auth-sessions-and-ownership.md`
- `docs/adr/0006-versioned-rest-api.md`

## Scope

In scope:

- backend health/readiness endpoint behavior;
- local Docker Compose stack for FastAPI and PostgreSQL;
- backend migration commands for local and hosted runtime use;
- CORS and cookie configuration for browser frontend integration;
- production-oriented backend Dockerfile;
- GitHub Actions backend verification workflow;
- runtime/deploy-readiness documentation.

Out of scope:

- actual Railway production deployment;
- frontend implementation;
- production monitoring and alerting;
- load testing against production-sized data;
- secret provisioning in Railway;
- CSV import, AI summaries, export/delete, and background scheduler work.

## Design Direction

Keep runtime readiness boring and explicit:

```text
developer machine / CI
  -> deterministic install
  -> migrate database
  -> start FastAPI
  -> health check
  -> backend checks
```

The local containerized path should use PostgreSQL so migration and SQLAlchemy behavior are tested closer to hosted deployment than SQLite-only tests can provide.

Runtime configuration must come from environment variables. Do not commit secrets, generated `.env` files, database volumes, or local container state.

## Decisions to Discuss Before Coding

- Health endpoint shape: simple liveness only, or separate liveness and readiness.
- Docker Compose scope: backend + PostgreSQL only for now, or include future frontend service placeholder.
- Migration timing: explicit command, container entrypoint, or hosted release command.
- Production image style: uv-based Python image, plain pip install, or separate lockfile-first build.
- CORS settings: same-site default only, or env-configurable allowlist now.
- CI timing: add backend CI before frontend exists, or wait until frontend tooling is added.

## Slice 1 - Health and Readiness Endpoint

Build:

- public liveness endpoint such as `GET /health`;
- optional DB readiness endpoint such as `GET /ready`;
- tests for response shape and unauthenticated access.

Success criteria:

- liveness does not require authentication;
- liveness does not depend on database availability unless intentionally designed that way;
- readiness, if included, checks database connectivity with a cheap query;
- error responses do not expose secrets or internal stack traces;
- OpenAPI loads successfully;
- `make backend-check` passes.

## Slice 2 - Migration Commands

Build:

- Makefile targets for Alembic upgrade/downgrade/current commands;
- documentation for running migrations locally;
- test or smoke command that runs migrations against a disposable database where practical.

Success criteria:

- `make backend-migrate` applies migrations to the configured database;
- `make backend-migration-current` or equivalent shows the current revision;
- migration commands use the project `uv` environment;
- commands work from the repo root;
- existing SQLite migration tests continue to pass.

## Slice 3 - Docker Compose Local PostgreSQL Stack

Build:

- `docker-compose.yml` or equivalent compose file for local PostgreSQL;
- persistent named volume for Postgres data;
- health check for Postgres;
- backend env example configured to use the compose Postgres host from the developer machine;
- `.env.example` updates if needed.

Success criteria:

- `docker compose up` starts PostgreSQL;
- backend can connect to PostgreSQL through `DATABASE_URL`;
- migrations can run against the compose database;
- host ports are documented;
- generated volumes and local `.env` files are ignored by git;
- no secrets are committed.

## Slice 4 - CORS and Cookie Runtime Configuration

Build:

- settings for allowed frontend origins;
- FastAPI CORS middleware configured for credentialed browser requests;
- tests for allowed and disallowed origins where practical;
- docs explaining local same-site vs cross-site cookie settings.

Success criteria:

- local frontend origin can call backend with `credentials: include`;
- unsafe requests can send the CSRF header;
- CORS allowlist is explicit and environment-driven;
- production cookies can use `Secure=true`;
- cross-site deployment requirements are documented: `SameSite=None`, `Secure=true`, explicit CORS allowlist, and CSRF verification.

## Slice 5 - Production Backend Dockerfile

Build:

- backend Dockerfile with a production target;
- uv-based dependency installation;
- non-root runtime user;
- minimal runtime command for FastAPI;
- Docker ignore rules for caches, virtualenvs, git data, test artifacts, and local env files.

Success criteria:

- image builds locally;
- container starts the backend;
- health endpoint succeeds in the running container;
- image does not include local secrets or `.venv`;
- runtime command uses production server settings appropriate for FastAPI.

## Slice 6 - Backend CI Workflow

Build:

- GitHub Actions workflow for backend checks on PRs to `development`;
- Python and uv setup;
- backend lint, typecheck, tests, and migration smoke;
- dependency cache where useful.

Success criteria:

- PRs to `development` run backend verification automatically;
- workflow uses deterministic dependency installation;
- workflow does not require secrets for normal backend tests;
- failures are visible in PR checks;
- local command and CI command stay aligned.

## Slice 7 - Runtime and Deploy-Readiness Documentation

Build:

- README or docs page updates for backend local runtime;
- Docker Compose instructions;
- migration workflow;
- required environment variables;
- Railway deployment notes without actually deploying.

Success criteria:

- a teammate can start the backend locally with PostgreSQL using documented commands;
- docs distinguish local development from hosted deployment;
- docs explain when to run migrations;
- docs list required env vars without real secret values;
- docs state that actual production deployment is a later step.

## Suggested Commit Breakdown

Preferred sequence:

1. `docs: add backend deploy readiness plan`
2. `feat: add backend health endpoints`
3. `chore: add backend migration commands`
4. `chore: add backend postgres compose stack`
5. `feat: configure backend cors`
6. `chore: add backend production dockerfile`
7. `ci: add backend verification workflow`
8. `docs: document backend runtime setup`

Acceptable adjustments:

- combine Docker Compose and migration command work if the commands are tiny;
- split CORS from cookie docs if config choices need review;
- defer production Dockerfile until after compose is proven locally.

## Phase Completion Criteria

- Backend can run locally against PostgreSQL.
- Migrations can be applied through a documented command.
- Health/readiness behavior is tested.
- Browser credentialed requests are supported by explicit CORS/cookie config.
- Backend image can be built and started locally.
- CI can verify backend linting, typing, tests, and migrations.
- No real deployment, secrets, database volumes, or local env files are committed.
