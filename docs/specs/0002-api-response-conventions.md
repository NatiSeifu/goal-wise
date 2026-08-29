# SPEC-0002: API Response Conventions

Status: Accepted
Last Updated: 2026-08-01
Related ADRs: ADR-0005, ADR-0006

## Purpose

Define the MVP HTTP response conventions for GoalWise's versioned JSON REST API.

## Success Responses

- Success responses return JSON objects, not bare arrays when metadata may be needed later.
- List endpoints should wrap arrays in an object.
- Response bodies must not include private data from another user.

Example list response:

```json
{
  "items": []
}
```

Example object response:

```json
{
  "item": {
    "id": "..."
  }
}
```

## Validation Errors

Use `422 Unprocessable Entity` for request validation failures.

Validation errors must identify the affected field when possible.

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "fields": {
      "target_cents": ["Must be greater than zero."]
    }
  }
}
```

## Authentication Errors

Use `401 Unauthorized` when the request has no valid authenticated session.

Examples:

- Missing session cookie.
- Unknown session token.
- Expired session.
- Revoked session.

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication required."
  }
}
```

## Ownership and Not Found Errors

Use `404 Not Found` when an authenticated user requests a private resource that either:

- Does not exist.
- Exists but belongs to another user.

This policy prevents the API from confirming whether another user's private financial resource exists.

```json
{
  "error": {
    "code": "not_found",
    "message": "Resource not found."
  }
}
```

## Forbidden Errors

Do not use `403 Forbidden` for MVP cross-user ownership failures.

Reserve `403 Forbidden` for future cases where the user is authenticated and known, but a broader role-based, plan-based, or account-state rule blocks the action.

## CSRF Errors

Use `403 Forbidden` for missing or invalid CSRF tokens on authenticated unsafe requests.

```json
{
  "error": {
    "code": "csrf_failed",
    "message": "Invalid request token."
  }
}
```

## Unexpected Errors

Use `500 Internal Server Error` for unexpected failures.

- Return a generic error message.
- Log only non-sensitive metadata.
- Do not log passwords, session tokens, CSRF tokens, raw transaction descriptions, exact balances, or exact goal amounts.

```json
{
  "error": {
    "code": "internal_error",
    "message": "Something went wrong."
  }
}
```

## Dashboard Pace Summary

The ready dashboard response includes `expected_savings_to_date_cents` in its
pace summary. This is the backend-calculated progress benchmark used to explain
an `At Risk` status. Clients must display or format this value and must not
reimplement the pace calculation.

## Verification

Required tests:

- Unauthenticated protected requests return `401`.
- Authenticated requests for missing private resources return `404`.
- Authenticated cross-user resource access returns `404`.
- Cross-user responses do not reveal whether the resource exists.
- Validation failures return `422` with field-level errors.
- Missing or invalid CSRF on authenticated unsafe requests returns `403` with `csrf_failed`.
- Unexpected exception handling returns a generic message and avoids sensitive logs.
