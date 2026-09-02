# GoalWise Architecture

GoalWise is a progressive MVP/PDR subset of the broader SRS. The current architecture proves the core planning loop: authenticate, enter or import one goal and manual financial assumptions, calculate an explainable weekly safe-to-spend result, store immutable snapshots, and render the dashboard. An accepted canonical planning CSV importer and optional explain-only AI layer sit outside the deterministic financial core.

This file holds the high-level system diagram. More focused diagrams and decision details live in:

- [Architecture decision process](docs/architecture-decision-process.md)
- [Architecture Decision Records](docs/adr/README.md)
- [Implementation Specs](docs/specs/README.md)
- [Backend design](DESIGN.md)

## High-Level System

```mermaid
flowchart TB
    User["User Browser"] --> Frontend["React + Vite Frontend"]

    subgraph Railway["Railway Hosted MVP"]
        Frontend -->|"HTTPS JSON /api/v1<br/>credentials included<br/>CSRF header on unsafe methods"| API["FastAPI Backend"]

        API --> Routers["API Routers"]
        Routers --> Schemas["Pydantic Schemas"]
        Routers --> Auth["Auth + CSRF Dependencies"]
        Auth --> Sessions[("Session Table<br/>hashed tokens")]

        Routers --> Services["Application Services"]
        Services --> Ownership["Ownership Checks"]
        Services --> Normalizer["Input Normalizer"]
        Services --> Pace["Pace Engine<br/>pace-v1 deterministic"]
        Services --> Snapshots["Snapshot Writer"]
        Services --> Dashboard["Dashboard Read Model"]

        Normalizer --> Pace
        Pace --> Snapshots
        Snapshots --> Dashboard

        Services --> Repos["Repositories"]
        Repos --> ORM["SQLAlchemy Models"]
        ORM --> DB[("Railway PostgreSQL")]
        Sessions --> DB
    end

    Frontend -->|"render backend values only"| DashboardUI["Dashboard + Forms"]
    Dashboard -->|"dashboard JSON"| Frontend

    subgraph Current["Current Planning Inputs"]
        CSV["Canonical Planning CSV Import"]
    end

    subgraph Deferred["Deferred Later Increments"]
        Transactions["Raw Transactions + Corrections"]
        AI["AI Summaries"]
        Export["Export + Account Deletion"]
        Scheduler["Monday Scheduler"]
    end

    CSV -->|"validated normalized inputs"| Services
    Transactions -. "future transaction inputs" .-> Services
    AI -. "aggregate snapshot payload only" .-> Snapshots
    Export -. "user-owned data" .-> Services
    Scheduler -. "creates weekly plans" .-> Services
```

## Boundary Rules

- The backend is the source of truth for authentication, authorization, validation, financial calculations, snapshots, dashboard metrics, and ownership checks.
- The React frontend must not duplicate pace-engine formulas or official dashboard metric formulas.
- The pace engine is deterministic and AI-free.
- Calculation snapshots are immutable and versioned.
- User-owned resource access is enforced server-side; cross-user private resource access returns `404`.
- Raw transaction import, export/delete, and background scheduling are deferred from the current MVP subset. Runtime AI is optional and explain-only; it cannot affect financial calculations or dashboard values.

## Deployment Shape

```mermaid
flowchart LR
    Browser["Browser"] --> FE["Railway Frontend<br/>React + Vite static build"]
    FE -->|"HTTPS /api/v1"| BE["Railway API<br/>FastAPI"]
    BE --> PG[("Railway PostgreSQL")]
    BE --> Env["Railway Service Variables"]
```

Hosted cookies use `Secure=true`. Same-site deployment uses `SameSite=Lax`; cross-site deployment uses `SameSite=None`, explicit CORS allowlists, credentials, and CSRF verification.
