# Evidence Map

Use this file to keep slide claims tied to project evidence.

| Slide | Claim | Repo evidence |
| --- | --- | --- |
| 1 | GoalWise answers whether a user is on pace for one savings goal. | `README.md`, `docs/PRODUCT_CONTEXT.md` |
| 2 | Current MVP scope is one active goal with manual financial assumptions. | `docs/PRODUCT_CONTEXT.md`, `docs/specs/0007-srs-traceability-and-mvp-scope.md`, `docs/adr/0007-mvp-deferrals.md` |
| 3 | React/Vite frontend calls FastAPI backend; backend owns validation, persistence, calculation, and dashboard values. | `ARCHITECTURE.md`, `DESIGN.md` |
| 4 | `pace-v1` is deterministic and AI-free. | `DESIGN.md`, `docs/adr/0002-deterministic-pace-engine-no-runtime-ai.md`, `backend/app/pace_engine/` |
| 5 | Calculation snapshots are immutable and versioned. | `docs/adr/0003-immutable-calculation-snapshots.md`, `docs/specs/0004-snapshot-json-schema.md`, `backend/app/models/calculation_snapshot.py` |
| 6 | Auth uses server-side sessions, CSRF protection, and ownership checks. | `docs/specs/0001-auth-session-security.md`, `docs/adr/0005-auth-sessions-and-ownership.md`, `backend/tests/api/test_cross_user_access.py` |
| 7 | Runtime AI explanations are optional, bounded, and cannot affect money outputs. | `docs/adr/0012-bounded-ai-explanation-layer.md`, `docs/specs/0011-ai-explanation-layer.md`, `backend/app/api/v1/ai_explanations.py` |
| 8 | Verification includes pace-engine golden tests, API tests, migration checks, and frontend checks. | `backend/tests/pace_engine/`, `backend/tests/api/`, `backend/tests/db/test_migrations.py`, `frontend/package.json` |
| 9 | The demo will show value path, safe failure, and engineering evidence. | Live app, seeded data, terminal test output, generated screenshots |

## Missing External Sources

Add course rubric, final report excerpts, and any instructor packet files here
before final claim polish. Do not add private credentials, real financial
records, or unreviewed AI output.
