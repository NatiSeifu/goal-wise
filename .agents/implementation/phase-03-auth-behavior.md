# Phase 3 - Auth Behavior

## Purpose

Implement the first usable authentication behavior on top of the persistence foundation.

This is an execution plan, not a new implementation contract. The source of truth remains:

- `docs/specs/0001-auth-session-security.md`
- `docs/specs/0002-api-response-conventions.md`
- `docs/specs/0005-date-time-semantics.md`
- `docs/adr/0005-auth-sessions-and-ownership.md`
- `.agents/plans/01-foundation-and-auth.md`

## Scope

In scope:

- password hashing and verification with Argon2id;
- email normalization;
- secure random session and CSRF token generation;
- token hashing for database storage;
- auth repositories for users, sessions, and login-attempt tracking;
- auth service behavior for register, login, logout, and current-session lookup;
- FastAPI application entrypoint and `/api/v1` route mounting;
- auth request/response schemas;
- HTTP-only session cookie behavior;
- CSRF verification for authenticated unsafe methods;
- login rate limiting after 5 failed attempts in 10 minutes;
- focused unit/API tests for the auth contract.

Out of scope:

- frontend pages;
- user-owned goal/financial resources;
- OAuth/social login;
- email verification and password reset;
- Redis-backed or distributed rate limiting;
- role-based authorization;
- production deployment execution.

## Design Decisions

Use a layered flow:

```text
API route -> schema validation -> auth service -> auth repositories -> SQLAlchemy models
```

Rationale:

- routes stay thin and HTTP-focused;
- services own auth rules and security decisions;
- repositories own SQLAlchemy queries;
- schemas own request/response shape;
- models remain persistence definitions, not business logic.

Use database-backed login-attempt tracking for the MVP. This keeps rate limiting portable
with SQLite locally and PostgreSQL on Railway. Redis can be introduced later only if the
MVP needs shared high-volume rate limiting across multiple backend instances.

## Slice 1 - Password Hashing and Email Normalization

Build:

- `backend/app/services/passwords.py`;
- `backend/app/services/email.py`;
- Argon2id password hashing and verification helpers;
- password length validation helper or service-level rule;
- normalized email helper used before uniqueness checks and login lookup.

Success criteria:

- valid passwords hash into Argon2-formatted strings;
- verification accepts the original password and rejects incorrect passwords;
- raw passwords are never returned by helpers;
- emails normalize consistently for registration and login;
- `make backend-check` passes.

## Slice 2 - Token Generation and Hashing

Build:

- `backend/app/services/tokens.py`;
- cryptographically secure opaque token generation;
- deterministic token hashing with `SESSION_SECRET`;
- separate helpers for session tokens and CSRF tokens if useful.

Success criteria:

- generated tokens are high entropy and URL-safe;
- token hashes are stable for the same token and secret;
- different tokens hash differently;
- tests prove raw tokens are not stored by downstream session creation;
- `make backend-check` passes.

## Slice 3 - Auth Repository Methods

Build:

- `backend/app/repositories/auth.py`;
- user lookup by normalized email;
- user creation;
- session creation with token hashes only;
- active session lookup by token hash;
- session revocation;
- login-attempt recording/reset for normalized email plus source address.

Success criteria:

- repositories use SQLAlchemy parameterized ORM queries;
- duplicate normalized email is handled predictably;
- session lookup rejects revoked or expired sessions at the repository/service boundary;
- login-attempt queries are testable with SQLite;
- `make backend-check` passes.

## Slice 4 - Login Attempt Persistence

Build:

- `backend/app/models/login_attempt.py`;
- Alembic migration adding login-attempt storage;
- repository tests for failed-attempt window behavior.

Suggested fields:

- `id`;
- `email_normalized`;
- `source_hash`;
- `failed_at`.

Success criteria:

- failed attempts are tracked without storing full source addresses;
- stale attempts outside the 10-minute window are ignored;
- successful login can clear/reset applicable attempts;
- migration upgrades and downgrades in SQLite tests;
- `make backend-check` passes.

## Slice 5 - Auth Service

Build:

- `backend/app/services/auth.py`;
- registration behavior;
- login behavior;
- logout behavior;
- current-session lookup behavior;
- explicit auth result/value objects as needed.

Success criteria:

- register stores an Argon2id password hash, not the raw password;
- register rejects duplicate email and passwords shorter than 12 characters;
- login returns generic failure for bad email or password;
- login creates a database-backed session with hashed session and CSRF tokens;
- logout revokes only the current session;
- expired, idle, or revoked sessions are rejected;
- `make backend-check` passes.

## Slice 6 - FastAPI App, Schemas, and Routes

Build:

- `backend/app/main.py`;
- `backend/app/api/v1/router.py`;
- `backend/app/api/v1/auth.py`;
- `backend/app/schemas/auth.py`;
- response/error helpers if needed for `docs/specs/0002-api-response-conventions.md`.

Endpoints:

- `POST /api/v1/auth/register`;
- `POST /api/v1/auth/login`;
- `POST /api/v1/auth/logout`;
- `GET /api/v1/me`.

Success criteria:

- routes validate request bodies with Pydantic schemas;
- login sets `goalwise_session` as an HTTP-only cookie;
- local cookies use `Secure=false`;
- production settings require `Secure=true`;
- auth errors use generic response messages;
- OpenAPI loads successfully;
- `make backend-check` passes.

## Slice 7 - Current User and CSRF Dependencies

Build:

- reusable current-session/current-user FastAPI dependency;
- CSRF dependency for authenticated unsafe methods;
- tests with a minimal protected route if no private MVP resource route exists yet.

Success criteria:

- missing, unknown, expired, or revoked sessions return `401`;
- missing or invalid CSRF on authenticated unsafe methods returns `403` with `csrf_failed`;
- safe methods do not require CSRF;
- dependencies expose authenticated user id to future service methods;
- `make backend-check` passes.

## Slice 8 - API Security Tests

Build API-level tests proving:

- register succeeds with unique email and valid password;
- register rejects duplicate email and short password;
- login succeeds with valid credentials;
- login fails generically with invalid credentials;
- login rate limiting blocks after 5 failed attempts within 10 minutes by normalized email and source;
- login sets an HTTP-only session cookie;
- `/api/v1/me` returns authenticated user data and current CSRF token;
- logout requires CSRF, revokes the session, and clears the cookie;
- protected unsafe requests reject missing or invalid CSRF.

Success criteria:

- tests do not log or assert raw secrets from database rows;
- tests use isolated SQLite databases;
- `make backend-check` passes.

## Suggested Commit Breakdown

Preferred sequence:

1. `docs: add auth behavior implementation plan`
2. `feat: add password and email auth helpers`
3. `feat: add auth token helpers`
4. `feat: add auth repositories`
5. `feat: add login attempt persistence`
6. `feat: add auth service behavior`
7. `feat: add auth api routes`
8. `test: cover auth api security behavior`

Acceptable adjustments:

- combine slices 1 and 2 if the helper modules stay small;
- combine repository and service tests only when separating them creates duplicate setup;
- keep migrations in their own commit when schema changes are involved.

## Phase Completion Criteria

Phase 3 is complete when:

- users can register, log in, call `/api/v1/me`, and log out through FastAPI;
- passwords are hashed with Argon2id;
- session and CSRF tokens are generated securely and stored only as hashes;
- the session cookie is HTTP-only and environment-aware;
- CSRF is enforced for authenticated unsafe methods;
- login rate limiting follows SPEC-0001;
- auth errors avoid account enumeration and sensitive details;
- no raw passwords or raw tokens are stored or logged;
- `make backend-check` passes.
