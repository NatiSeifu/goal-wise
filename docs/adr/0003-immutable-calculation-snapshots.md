# ADR-0003: Use Immutable Calculation Snapshots

## Status

Accepted

## Context

GoalWise users need to inspect how a weekly safe-to-spend amount was calculated. The system also needs to explain changes after edits to goals, income, expenses, or financial profile data. If calculation results are only stored as current mutable fields, the team cannot audit prior outputs or compare changes reliably.

## Decision

Create an immutable `CalculationSnapshot` after each valid input change when required inputs are complete. Each snapshot stores:

- Authenticated `user_id`.
- Related `goal_id`.
- Formula version.
- Trigger.
- Stable normalized input JSON.
- Structured result JSON.
- UTC calculation timestamp.

Snapshots are inserted and never updated.

The exact JSON shapes are defined in [SPEC-0004: Snapshot JSON Schema](../specs/0004-snapshot-json-schema.md). Snapshot inputs include user-authored planning labels for explainability, but transaction entries use minimized calculation facts and do not copy raw transaction descriptions into immutable history.

```mermaid
sequenceDiagram
    participant UI as Form or Dashboard
    participant API as FastAPI API
    participant Service as Application Service
    participant Engine as Pace Engine
    participant DB as Database

    UI->>API: Save valid goal or financial input
    API->>Service: Apply change for current user
    Service->>DB: Persist user-owned record
    Service->>DB: Load normalized inputs
    alt required inputs incomplete
        Service-->>API: Missing-input state
    else required inputs complete
        Service->>Engine: calculate pace-v1
        Engine-->>Service: Pace result
        Service->>DB: Insert calculation snapshot
        Service-->>API: Updated dashboard summary
    end
    API-->>UI: JSON response
```

## Options Considered

| Option | Tradeoffs |
| --- | --- |
| Immutable snapshots | Strong auditability, explainability, and change comparison. Uses more storage and requires stable JSON normalization. |
| Store only latest result on goal/profile rows | Simpler schema, but loses history and makes "why did this change?" difficult. |
| Recompute all historical values on demand | Avoids snapshot storage, but historical outputs can change if formulas or input normalization change. |
| Event sourcing for every input mutation | Very strong audit trail, but too much complexity for MVP. |

## Consequences

Positive:

- Dashboard details can come from the backend's recorded calculation.
- Formula changes can be introduced under a new version without rewriting old results.
- The latest two snapshots can be compared to explain changed input categories and safe-to-spend deltas.

Negative:

- Snapshot JSON shape must remain stable.
- Sensitive financial values must be protected in logs and access controls.
- Raw transaction descriptions are kept out of immutable snapshots, so detailed transaction insight must query the user-owned `Transaction` table.
- Storage grows with each valid input change.

## Verification

- Snapshot immutability test proves existing snapshots are not edited.
- Snapshot schema tests prove required keys are present and raw transaction descriptions are absent.
- API integration test proves valid input changes create new snapshots.
- Dashboard endpoint reads from latest snapshot rather than recalculating in the frontend.
