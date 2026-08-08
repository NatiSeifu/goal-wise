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
COOKIE_SECURE=true
COOKIE_SAMESITE=Lax or None
ALLOWED_FRONTEND_ORIGIN
ENVIRONMENT=production
```

Frontend service variables:

```text
VITE_API_BASE_URL
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

If browser behavior treats the frontend and API as cross-site, use:

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

Frontend:

- Build command: `npm run build`.
- Static output directory: Vite `dist`.
- API base URL comes from `VITE_API_BASE_URL`.

Backend:

- Start FastAPI with the Railway-provided `PORT`.
- Read all runtime configuration from environment variables.
- Expose a lightweight health endpoint for demo monitoring.

## Security Requirements

- Hosted cookies must use `Secure=true`.
- Session tokens must remain HTTP-only cookies.
- CORS must allow only the deployed frontend origin.
- CSRF remains required for authenticated unsafe methods.
- Do not commit Railway secrets or local `.env` files.

## Verification

Required checks:

- Frontend loads over HTTPS.
- Frontend can call `/api/v1/me` with credentials.
- Backend connects to Railway PostgreSQL through `DATABASE_URL`.
- Alembic migration state is current.
- Register, login, logout, and CSRF-protected unsafe request flow works in the hosted environment.
- CORS rejects an unapproved origin.
- Health endpoint is reachable during the demo window.
