# Slide 5: Technical Approach, Architecture, AI, and ADR

## Slide Goal

Show that GoalWise uses a deterministic financial core with an optional AI explanation layer. The main message is: AI may help explain, but it does not calculate safe-to-spend.

## Suggested Slide Layout

Left side: architecture image.

Right side: concise bullets:

**Technical Stack**

- React + Vite frontend
- FastAPI backend with REST `/api/v1`
- SQLAlchemy + Alembic persistence
- PostgreSQL on Railway; SQLite for local/test
- Argon2id auth, HTTP-only sessions, CSRF
- Mermaid ADR/spec documentation

**AI Boundary**

- AI may summarize deterministic results later
- AI may assist transaction classification later
- AI never calculates or overrides safe-to-spend
- Pace engine remains deterministic and testable

**ADR Summary**

ADR decision: use a deterministic `pace-v1` calculation engine with optional AI explanations at the edge.

Alternatives considered:

- AI-based calculations: flexible, but harder to verify and risks inconsistent money guidance.
- Deterministic calculations only: safest and easiest to test, but less user-friendly for explanations.
- Deterministic calculations with optional AI explanations: keeps money logic auditable while allowing plain-language summaries later.

Chosen approach:

Use deterministic calculations as the source of truth. Add AI only as an optional explanation/classification layer that consumes validated, minimized data.

## Short Presenter Script

GoalWise separates the user experience from the financial core. The React frontend sends user-entered goals and financial assumptions to a FastAPI backend. The backend validates ownership, normalizes the inputs, and calls a deterministic pace engine. That engine produces safe-to-spend, shortfall, and pace status, then stores immutable calculation snapshots.

CSV import and LLM summaries are shown as edge components. CSV can become another input source later, and the LLM can summarize results or help classify transactions, but neither is allowed to calculate or override the safe-to-spend amount. That boundary is the core architecture decision.

## Asset

Use this PNG for the high-level architecture:

```text
docs/slides/assets/slide-5-architecture.png
```

Use this PNG if you want the behavioral/data-flow sequence view:

```text
docs/slides/assets/slide-5-sequence-recalculate.png
```
