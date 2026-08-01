# 01 - Foundation and Auth Plan

## Objective

Create the application foundation and secure enough authentication for the MVP. This plan should leave the repo with a runnable backend, a connected frontend shell, migrations, test setup, and protected API conventions.

## Backend Foundation

- Create a FastAPI backend with routes mounted under `/api/v1`.
- Add SQLAlchemy models, database session management, and Alembic migrations.
- Configure SQLite for local development and tests while preserving Railway PostgreSQL-compatible column types and constraints.
- Add Pydantic request and response schemas.
- Add centralized error handling for validation, auth failures, ownership failures, and unexpected exceptions.
- Add configuration via environment variables for database URL, session secret, cookie security flags, and allowed frontend origin.
- Prepare deployment configuration for Railway services and Railway PostgreSQL.

## Frontend Foundation

- Scaffold a React + Vite frontend with routes for sign in, register, and dashboard.
- Add an API client wrapper that sends credentials and handles validation errors consistently.
- Add a protected-route pattern that redirects unauthenticated users to sign in.
- Keep initial UI minimal: form pages, app shell, and dashboard placeholder.

## Auth Behavior

- Implement `POST /api/v1/auth/register`.
  - Require unique email and password length of at least 12 characters.
  - Normalize email for uniqueness.
  - Store only an Argon2id password hash.
- Implement `POST /api/v1/auth/login`.
  - Return a generic error for invalid credentials.
  - Rate-limit after 5 failed attempts within 10 minutes by normalized email and source address.
  - Create a database-backed server-side session.
  - Store only a hash of the opaque session token.
  - Set the raw session token in a secure HTTP-only cookie.
  - Return a per-session CSRF token for unsafe methods.
- Implement `POST /api/v1/auth/logout`.
  - Require a valid CSRF token.
  - Revoke the current session and clear the cookie.
- Implement `GET /api/v1/me`.
  - Return authenticated user id, email, time zone, and current CSRF token.
- Add a reusable FastAPI dependency for `current_user`.
- Require `X-CSRF-Token` on authenticated `POST`, `PUT`, `PATCH`, and `DELETE` requests.

## Ownership and Security Conventions

- Every user-owned repository query must filter by `user_id`.
- Service methods must accept the authenticated user id explicitly.
- Protected endpoints must never trust `user_id` from request bodies.
- Missing private resources and cross-user private resource access must return `404`.
- Reserve `403` for future role-based or account-state authorization failures.
- Logs must exclude passwords, session tokens, and exact financial values.
- Local development may use `Secure=false` cookies over HTTP.
- Hosted Railway environments must use `Secure=true` cookies. Prefer same-site frontend/backend hosting with `SameSite=Lax`.
- Sessions must expire after 30 minutes of inactivity and no later than 24 hours after issuance.
- Login rate limiting is in MVP scope.

## Tests

- Register succeeds with unique email and valid password.
- Register rejects duplicate email and short password.
- Login succeeds with valid credentials and fails generically with invalid credentials.
- Login rate limiting blocks an account and source after 5 failed attempts within 10 minutes without revealing whether the email exists.
- Logout invalidates the current session.
- Sessions expire after 30 minutes of inactivity and no later than 24 hours after issuance.
- State-changing authenticated requests reject missing or invalid CSRF tokens.
- Session storage stores token hashes, not raw session tokens.
- Protected endpoint rejects unauthenticated requests.
- Cross-user access test proves one user receives `404` when trying to fetch or mutate another user's private resource.

## Completion Criteria

- Backend starts locally and exposes OpenAPI docs in development.
- Frontend can register, log in, log out, and call `/api/v1/me`.
- Initial migration creates user/session tables.
- Auth tests pass.
