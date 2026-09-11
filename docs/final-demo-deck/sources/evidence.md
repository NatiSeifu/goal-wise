# Evidence Map

Use this file to keep slide claims tied to project evidence.

| Slide | Claim | Repo evidence |
| --- | --- | --- |
| 1 | GoalWise takes a user from registration and guided setup to one goal and a weekly plan. | `frontend/e2e/auth-and-setup.spec.ts`, `frontend/e2e/support/flows.ts`, `README.md` |
| 2 | The product answers whether one user can stay on pace for one savings goal. | `docs/PRODUCT_CONTEXT.md`, `docs/specs/0007-srs-traceability-and-mvp-scope.md` |
| 3 | React/Vite frontend calls FastAPI backend; backend owns validation, persistence, calculation, and dashboard values. | `ARCHITECTURE.md`, `DESIGN.md` |
| 4 | `pace-v1` is deterministic and independent from runtime AI. | `DESIGN.md`, `docs/adr/0002-deterministic-pace-engine-no-runtime-ai.md`, `backend/app/pace_engine/` |
| 5 | Calculation snapshots are immutable and versioned. | `docs/adr/0003-immutable-calculation-snapshots.md`, `docs/specs/0004-snapshot-json-schema.md`, `backend/app/models/calculation_snapshot.py` |
| 6 | Auth uses server-side sessions, CSRF protection, and ownership checks. | `docs/specs/0001-auth-session-security.md`, `docs/adr/0005-auth-sessions-and-ownership.md`, `backend/tests/api/test_cross_user_access.py` |
| 7 | Planning CSV import previews and rejects invalid files before commit. | `frontend/e2e/planning-import.spec.ts`, `backend/app/api/v1/planning_import.py` |
| 8 | Runtime AI explanations are optional, bounded, and cannot affect money outputs. | `docs/adr/0012-bounded-ai-explanation-layer.md`, `docs/specs/0011-ai-explanation-layer.md`, `backend/app/api/v1/ai_explanations.py` |
| 9 | Verification and delivery evidence includes tests, GitHub CI, Railway, and seeded demo data. | `backend/tests/`, `frontend/package.json`, `.github/workflows/`, `docs/adr/0009-railway-deployment.md` |

## Missing External Sources

Add course rubric, final report excerpts, and any instructor packet files here
before final claim polish. Do not add private credentials, real financial
records, or unreviewed AI output.
