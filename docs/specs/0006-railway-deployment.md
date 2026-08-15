# SPEC-0006: Railway Deployment

Status: Accepted
Last Updated: 2026-08-01
Related ADRs: ADR-0008, ADR-0009
Related Specs: SPEC-0001, SPEC-0002

## Purpose

Define the deployment contract for the GoalWise course MVP on Railway.

## Services

Railway project services:

- `frontend`: React + Vite static site or static frontend service.
- `api`: FastAPI web service.
- `postgres`: Railway PostgreSQL database.

## Required Environment Variables

Backend service variables:

```text
DATABASE_URL
SESSION_SECRET
SECURE_COOKIES=true
COOKIE_SAMESITE=Lax or None
ALLOWED_FRONTEND_ORIGIN
ENVIRONMENT=staging or production
```

Frontend service variables:

```text
API_PROXY_TARGET
VITE_API_BASE_URL optional; leave unset/empty for same-origin API calls
```

Local development may use `.env` files. Hosted secrets must be configured as Railway service variables.

## Domain Policy

Preferred course/demo setup:

```text
Frontend: https://app.<team-domain>
API:      https://api.<team-domain>
Cookie:   SameSite=Lax, Secure=true, HttpOnly=true
```

Acceptable Railway-provided setup:

```text
Frontend: https://<frontend>.up.railway.app
API:      https://<api>.up.railway.app
```

The browser should still call the API through the frontend origin:

```text
Browser -> https://<frontend>.up.railway.app/api/v1/*
Frontend Caddy -> API_PROXY_TARGET -> api service
```

This keeps session cookies first-party for the browser and avoids mobile Safari
cross-site cookie behavior. The public API domain may remain available for
health checks and diagnostics, but the React app should not call it directly in
hosted environments.

If browser behavior treats the frontend and API as cross-site because the React
app calls the API public domain directly, use:

```text
SameSite=None
Secure=true
HttpOnly=true
```

Cross-site setup also requires:

- explicit `ALLOWED_FRONTEND_ORIGIN`;
- credentialed CORS;
- CSRF verification on unsafe authenticated requests.

Same-site deployment is preferred because it keeps cookies and CSRF simpler.

## Database

- Use Railway PostgreSQL for hosted environments.
- Use SQLite only for local development and automated tests.
- Use local PostgreSQL through Docker Compose for deploy-readiness smoke checks.
- SQLAlchemy models and Alembic migrations must stay PostgreSQL-compatible.
- Run migrations against Railway PostgreSQL before demo use.

Migration commands are exposed from the repo root:

```text
make backend-migrate
make backend-migration-current
make backend-migration-downgrade
```

These commands run Alembic through the backend `uv` environment and use the configured `DATABASE_URL`.

## Build and Runtime

Railway should deploy GoalWise as an isolated monorepo with one Railway service
per application root:

```text
api root directory: /backend
frontend root directory: /frontend
```

Frontend:

- Use `frontend/Dockerfile`.
- The Dockerfile builds Vite output and serves `dist` with Caddy.
- Hosted builds should leave `VITE_API_BASE_URL` unset or empty so browser API
  calls use same-origin `/api/*` paths.
- Caddy proxies `/api/*` to `API_PROXY_TARGET`.

Backend:

- Use `backend/Dockerfile`.
- Start FastAPI with the Railway-provided `PORT`.
- Read all runtime configuration from environment variables.
- Expose a lightweight health endpoint for demo monitoring.

## Staging Environment

Recommended staging variables:

Backend `api` service:

```text
ENVIRONMENT=staging
DATABASE_URL=${{Postgres.DATABASE_URL}}
SESSION_SECRET=<long random value>
SECURE_COOKIES=true
COOKIE_SAMESITE=none
ALLOWED_FRONTEND_ORIGIN=https://<frontend-staging-domain>
```

Frontend service:

```text
API_PROXY_TARGET=https://<api-staging-domain>
VITE_API_BASE_URL=
```

Use exact generated Railway domains without trailing slashes. Prefer Railway
private networking for `API_PROXY_TARGET` when available. With the frontend
same-origin proxy in place, `COOKIE_SAMESITE=lax` is acceptable; `none` remains
valid only when paired with `SECURE_COOKIES=true`.

## Security Requirements

- Hosted cookies must use `Secure=true`.
- Session tokens must remain HTTP-only cookies.
- CORS must allow only the deployed frontend origin.
- CORS must allow credentials and the `X-CSRF-Token` request header.
- CSRF remains required for authenticated unsafe methods.
- Do not commit Railway secrets or local `.env` files.

## Verification

Required checks:

- Frontend loads over HTTPS.
- Frontend can call same-origin `/api/v1/auth/me` with credentials.
- Backend connects to Railway PostgreSQL through `DATABASE_URL`.
- Alembic migration state is current.
- Register, login, logout, and CSRF-protected unsafe request flow works in the hosted environment.
- CORS rejects an unapproved origin.
- Health endpoint is reachable during the demo window.
