# 01 - Foundation and Auth Plan

## Objective

Create the application foundation and secure enough authentication for the MVP. This plan should leave the repo with a runnable backend, a connected frontend shell, migrations, test setup, and protected API conventions.

## Backend Foundation

- Create a FastAPI backend with routes mounted under `/api/v1`.
- Add SQLAlchemy models, database session management, and Alembic migrations.
- Configure SQLite for local development and tests while preserving PostgreSQL-compatible column types and constraints.
- Add Pydantic request and response schemas.
- Add centralized error handling for validation, auth failures, ownership failures, and unexpected exceptions.
- Add configuration via environment variables for database URL, session secret, cookie security flags, and allowed frontend origin.

## Frontend Foundation

- Scaffold a React or Next.js frontend with routes for sign in, register, and dashboard.
- Add an API client wrapper that sends credentials and handles validation errors consistently.
- Add a protected-route pattern that redirects unauthenticated users to sign in.
- Keep initial UI minimal: form pages, app shell, and dashboard placeholder.

## Auth Behavior

- Implement `POST /api/v1/auth/register`.
  - Require unique email and password length of at least 12 characters.
  - Normalize email for uniqueness.
  - Store only a salted password hash.
- Implement `POST /api/v1/auth/login`.
  - Return a generic error for invalid credentials.
  - Create a secure HTTP-only session cookie.
- Implement `POST /api/v1/auth/logout`.
  - Revoke the current session and clear the cookie.
- Implement `GET /api/v1/me`.
  - Return authenticated user id, email, and time zone.
- Add a reusable FastAPI dependency for `current_user`.

## Ownership and Security Conventions

- Every user-owned repository query must filter by `user_id`.
- Service methods must accept the authenticated user id explicitly.
- Protected endpoints must never trust `user_id` from request bodies.
- Logs must exclude passwords, session tokens, and exact financial values.
- Add rate limiting only if the selected stack already has a simple local middleware; otherwise document it as post-MVP hardening.

## Tests

- Register succeeds with unique email and valid password.
- Register rejects duplicate email and short password.
- Login succeeds with valid credentials and fails generically with invalid credentials.
- Logout invalidates the current session.
- Protected endpoint rejects unauthenticated requests.
- Cross-user access test proves one user cannot fetch another user's private placeholder resource once goal endpoints exist.

## Completion Criteria

- Backend starts locally and exposes OpenAPI docs in development.
- Frontend can register, log in, log out, and call `/api/v1/me`.
- Initial migration creates user/session tables.
- Auth tests pass.

