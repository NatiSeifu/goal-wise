# SPEC-0001: Auth and Session Security

Status: Accepted
Last Updated: 2026-08-01
Related ADRs: ADR-0005, ADR-0008

## Purpose

Define the MVP authentication, session storage, browser cookie, and CSRF behavior for GoalWise.

## Passwords

- Hash passwords with Argon2id.
- Require passwords of at least 12 characters.
- Normalize email addresses before uniqueness checks.
- Return generic login failure messages for invalid credentials.
- Rate-limit login after 5 failed attempts within 10 minutes by normalized email and source address.
- Never log passwords, password hashes, session tokens, CSRF tokens, or full email addresses.

## Session Storage

Use database-backed server-side sessions. The browser receives a raw opaque session token, but the database stores only a hash of that token.

Session table fields:

```text
sessions
  id uuid primary key
  user_id uuid not null references users(id)
  session_token_hash string not null unique
  csrf_token_hash string not null
  created_at datetime not null
  last_seen_at datetime not null
  expires_at datetime not null
  revoked_at datetime nullable
  user_agent_hash string nullable
  ip_prefix_hash string nullable
```

Session rules:

- Generate session tokens using a cryptographically secure random source.
- Store only `session_token_hash`; never store the raw session token.
- Reject sessions that are expired or revoked.
- Expire sessions after 30 minutes of inactivity.
- Expire sessions no later than 24 hours after issuance.
- Update `last_seen_at` on authenticated requests, with throttling allowed to avoid excessive writes.
- Revoke the current session on logout by setting `revoked_at`.
- Clear the browser cookie on logout.

## Login Rate Limiting

The login endpoint must rate-limit brute-force attempts.

Rules:

- Track failed login attempts by normalized email and source address.
- Apply the limit after 5 failed attempts within 10 minutes.
- Return a generic login failure or throttling response that does not reveal whether the email exists.
- Successful login clears or resets the applicable failed-attempt counter.
- The rate-limit store may be database-backed for the MVP.
- Logs must not include full email addresses, passwords, or raw session tokens.

## Cookie Rules

Cookie name:

```text
goalwise_session
```

Local development cookie settings:

```text
HttpOnly=true
Secure=false
SameSite=Lax
Path=/
```

Hosted production cookie settings:

```text
HttpOnly=true
Secure=true
SameSite=Lax
Path=/
```

Use `SameSite=Lax` when the frontend and backend are same-site. If they are hosted cross-site, use:

```text
HttpOnly=true
Secure=true
SameSite=None
Path=/
```

Cross-site hosting also requires explicit CORS allowlists and CSRF verification. Same-site hosting is preferred for the MVP.

Do not store session tokens in `localStorage` or `sessionStorage`.

## CSRF Rules

CSRF protection is required because browser cookies are sent automatically.

- Generate one CSRF token per session.
- Store only `csrf_token_hash` in the session row.
- Return the raw CSRF token in the login response.
- Return the current raw CSRF token from `GET /api/v1/me` for authenticated sessions.
- Require the frontend to send the token in `X-CSRF-Token` for authenticated `POST`, `PUT`, `PATCH`, and `DELETE` requests.
- Reject missing, invalid, expired-session, or revoked-session CSRF checks.
- Do not require CSRF for `GET`, `HEAD`, or `OPTIONS`.

## Frontend Requirements

The React + Vite frontend must:

- Send API requests with `credentials: "include"` when authentication is needed.
- Keep the CSRF token in application memory.
- Refresh the CSRF token from `/api/v1/me` after page reload.
- Include `X-CSRF-Token` on authenticated unsafe methods.
- Redirect unauthenticated users from protected routes to sign in.

## Verification

Required tests:

- Register stores an Argon2id password hash and never stores the raw password.
- Login creates a session row with `session_token_hash` and `csrf_token_hash`.
- Login rate limiting blocks after 5 failed attempts within 10 minutes by normalized email and source address.
- Login rate limiting does not reveal whether the email exists.
- Login sets an HTTP-only session cookie.
- Local settings use `Secure=false`; hosted settings use `Secure=true`.
- `/api/v1/me` returns the authenticated user and current CSRF token.
- Logout requires CSRF, revokes the session, and clears the cookie.
- Authenticated `POST`, `PUT`, `PATCH`, and `DELETE` reject missing or invalid CSRF tokens.
- Protected endpoints reject expired or revoked sessions.
- Sessions expire after 30 minutes of inactivity and no later than 24 hours after issuance.
- Session tokens are not stored in `localStorage` or `sessionStorage`.
