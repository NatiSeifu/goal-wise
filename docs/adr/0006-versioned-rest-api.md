# ADR-0006: Expose a Versioned REST API for the MVP

## Status

Accepted

## Context

The frontend needs predictable operations for auth, the active goal, financial profile, income sources, planned expenses, dashboard data, and latest calculation snapshot. The MVP does not require bidirectional streaming, complex graph traversal, or multiple client types with different query shapes.

## Decision

Expose a versioned JSON REST API under `/api/v1`. Keep endpoint names resource-based and predictable. Return JSON objects rather than bare arrays where metadata may be needed later.

```mermaid
flowchart LR
    UI[Frontend] --> Auth[/api/v1/auth/*]
    UI --> Me[/api/v1/me]
    UI --> Goals[/api/v1/goals]
    UI --> Profile[/api/v1/financial-profile]
    UI --> Income[/api/v1/income-sources]
    UI --> Expenses[/api/v1/planned-expenses]
    UI --> Dashboard[/api/v1/dashboard]
    UI --> Snapshots[/api/v1/calculation-snapshots/latest]
```

## Options Considered

| Option | Tradeoffs |
| --- | --- |
| Versioned REST | Predictable, easy to test, fits CRUD-heavy MVP, and aligns with FastAPI/OpenAPI docs. |
| GraphQL | Flexible client queries, but unnecessary complexity for the MVP resource model. |
| RPC-style endpoints | Simple for actions, but weaker resource consistency and harder long-term discoverability. |
| WebSocket-first API | Useful for real-time collaboration, but not needed for manual budgeting forms and dashboard refreshes. |

## Consequences

Positive:

- OpenAPI documentation can describe the contract.
- Tests can target stable endpoint names and response shapes.
- The frontend can use a small API client wrapper.

Negative:

- Some dashboard read models are not pure CRUD resources.
- Versioning discipline is required if response contracts change.

## Verification

- API integration tests cover MVP endpoints.
- Validation failures return `422` with field-level errors.
- Unauthorized requests return `401`.
- Missing private resources and cross-user ownership failures return `404` without leaking financial content.
- `403` is reserved for future role-based or account-state authorization failures.
