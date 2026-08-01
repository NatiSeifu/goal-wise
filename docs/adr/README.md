# Architecture Decision Records

This directory contains Architecture Decision Records for GoalWise.

ADRs preserve why the architecture is shaped the way it is. Diagrams use Mermaid so they can render in Markdown tools that support Mermaid.

## Index

| ADR | Title | Status |
| --- | --- | --- |
| [0001](0001-layered-modular-monolith.md) | Use a Layered Modular Monolith | Accepted |
| [0002](0002-deterministic-pace-engine-no-runtime-ai.md) | Keep the Pace Engine Deterministic and AI-Free for MVP | Accepted |
| [0003](0003-immutable-calculation-snapshots.md) | Use Immutable Calculation Snapshots | Accepted |
| [0004](0004-money-integer-cents-and-formula-versioning.md) | Store Money as Integer Cents and Use Formula Versioning | Accepted |
| [0005](0005-auth-sessions-and-ownership.md) | Use Server-Side Sessions and Ownership Checks | Accepted |
| [0006](0006-versioned-rest-api.md) | Expose a Versioned REST API for the MVP | Accepted |
| [0007](0007-mvp-deferrals.md) | Defer Bank Sync, CSV Import, and AI Summaries from MVP | Accepted |

## Template

Each ADR uses this shape:

- Status
- Context
- Decision
- Options Considered
- Consequences
- Verification

