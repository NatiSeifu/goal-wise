**GoalWise**

**Security Review**

MSCS 2101 · Module 8 · Group 3

*Repository: github.com/NatiSeifu/goal-wise · Reviewed: August 30, 2026*

**1. Threat Model — Feature: Financial Input & Goal Mutation Endpoints**

------------------------------------------------------------------------

|  |  |
|----|----|
| Asset | A user's authenticated session and their private financial planning data — goal targets, saved amounts, income sources, planned expenses, and the calculation snapshots derived from them. |
| Entry point | POST/PATCH/DELETE /api/v1/goals, /api/v1/financial-inputs — all state-changing requests that rely on the browser's session cookie. |
| Threats (STRIDE) | Tampering — Cross-Site Request Forgery against authenticated endpoints. Because the session is a cookie, a malicious site could induce a logged-in user's browser to submit a request that alters goal data or financial inputs without the user's knowledge. Elevation of Privilege — Insecure Direct Object Reference (IDOR/BOLA): if an endpoint doesn't verify the requesting user owns the resource, one authenticated user could read or modify another user's goal or financial data by supplying a different ID. |
| Mitigations | CSRF: unsafe methods require a per-session CSRF token, generated with secrets.token_urlsafe, stored server-side only as an HMAC hash (app/services/tokens.py), and compared with hmac.compare_digest to avoid timing attacks. The session cookie itself is HttpOnly. IDOR/ownership: every service function that reads or mutates a Goal or financial input is scoped by the authenticated session's user_id at the query level (e.g. get_active_goal_for_user, update_goal_for_user in app/services/goal_inputs.py) — not by trusting a client-supplied ID. |
| Residual risk | Low-Medium. CSRF and ownership checks are enforced in the service layer, which is good — but this review only traced the goals/financial-inputs path by hand. We have not yet written an automated negative-authorization test (e.g., “User B requests User A's goal, expect 403/404”) for every mutating endpoint, so a future endpoint added without following the same pattern could regress silently. Recommended as a follow-up before Final. |

**2. SAST Scan — Semgrep**

------------------------------------------------------------------------

We ran Semgrep 1.175.0 against the full repository using the official Python, TypeScript, JavaScript, Dockerfile, and secrets rule packs (852 rules, 196 files scanned). The hosted semgrep.dev “auto” config endpoint was not reachable from our environment, so we pulled the same open-source rules directly from the official semgrep/semgrep-rules GitHub repository and ran them locally — same rule content, offline source.

**Findings summary**

| **\#** | **Severity** | **Rule / issue** | **Location** | **Action** |
|----|----|----|----|----|
| 1 | Error | Dockerfile: production stage has no USER directive (runs as root) | frontend/Dockerfile:30 | Fixed — added non-root user |
| 2 | Warning | Dockerfile: build ARG looks like it could hold a secret | frontend/Dockerfile:5 | Triaged — false positive (VITE_API_BASE_URL is a public config value, not a credential) |
| 3 | Warning | Maintainability: property access flagged as function-without-parens | backend/app/core/config.py:44 | Triaged — false positive; is_production is an intentional @property |
| 4 | Warning | Maintainability: return outside function (dataclass pattern) | backend/app/pace_engine/types.py:143 | Triaged — false positive; return is inside \_\_post_init\_\_ |
| 5 | Warning | Correctness: discouraged key-stringify pattern | resources.test.ts:25, seed-user-stories.mjs:265 | Triaged — false positive; flagged code reads a Headers object, not a stringify-keys pattern |
| 6 | Warning × 12 | React/i18n: hardcoded JSX label text (not internationalized) | LoginRoute.tsx, RegisterRoute.tsx, FinancialInputsRoute.tsx, GoalRoute.tsx | Triaged — not applicable; MVP is explicitly English-only, single time zone default (SRS §2.7) |

*1 real finding fixed (missing non-root USER in the frontend Docker image); 21 findings triaged as false positives or not applicable to this project's scope. Full JSON output retained by the team.*

**3. AI-Generated Code Review & Dependency Verification**

------------------------------------------------------------------------

**OWASP-style code review**

| **Check** | **Result** |
|----|----|
| Injection | No string-concatenated SQL found. All queries go through SQLAlchemy's ORM/query builder with bound parameters. ✓ |
| Missing auth / ownership | Traced goals and financial-inputs routes by hand (see §1) — all mutating endpoints require an authenticated session and scope queries by user_id. ✓ (automated negative-auth tests recommended as follow-up) |
| Hard-coded secrets | None found in source. SESSION_SECRET, DATABASE_URL, and cookie settings are all read from environment variables; .env.example files contain clearly-labeled placeholder/dev-only values, not real credentials. ✓ |
| Unsafe input handling | Request bodies are validated through Pydantic schemas before reaching service logic; money is stored as integer cents, never floats, avoiding a class of rounding/precision bugs. ✓ |
| Insecure defaults (CORS/cookies) | CORS is restricted to a single configured allowed_frontend_origin (not a wildcard), with allow_credentials=True paired deliberately with that restriction and a scoped header allowlist. Production settings explicitly reject the default/local SESSION_SECRET at startup (config.py). ✓ |

**Dependency verification (slopsquatting check)**

We checked every entry in backend/pyproject.toml and frontend/package.json. Frontend dependencies (React 19, Vite, TypeScript, Vitest, react-router-dom, etc.) are all standard, well-known packages with no naming irregularities.

**One backend dependency needed a closer look: httpx2 (listed as a dev dependency, presumably for API testing). This name is one character off from httpx, the long-standing standard async HTTP client used throughout the FastAPI ecosystem — exactly the kind of plausible-but-wrong name an AI assistant can produce.**

On checking, httpx2 does appear to be a real, currently-registered PyPI package with a GitHub presence, described as a 2026 successor/rebrand of httpx under new stewardship. However, we could not fully corroborate this from independent, authoritative sources, and third-party package-security scanners flagged some recent httpx2 releases with embedded web-service credentials and, in at least one version, a high-severity vulnerability. Given the package's very recent history and these scanner findings, we are treating this as an open risk rather than a verified-safe dependency — it is not a clear-cut nonexistent “slopsquat,” but it is also not something we're comfortable trusting on name recognition alone.

Action: pin httpx2 to an exact, hash-verified version rather than a \>= range, or fall back to the original, long-established httpx package for our test client until we've independently confirmed the new package's provenance and security history. This is tracked as an open item below.

**4. Fixes Applied & Resilience Measure**

------------------------------------------------------------------------

**Fixes this week**

- Added a non-root USER directive to the frontend production Docker image (previously ran as root in the Caddy stage).

- Documented the httpx2 dependency as an open item — pin to an exact version or revert to httpx pending independent verification (not yet resolved).

- Recommended: add automated negative-authorization tests (“User B cannot read/modify User A's goal”) for every mutating endpoint, not just manual code-path tracing (not yet resolved).

**Resilience measure**

GoalWise's readiness endpoint (GET /ready) explicitly checks the database connection and returns a 503 with a clear { "status": "unavailable" } body if it's unreachable, instead of letting requests fail unpredictably. Separately, by design (ADR-0002), the MVP runtime has zero dependency on any external AI service — AI is used only at design time (drafting diagrams, ADRs, tests), never in the running application. That means there is currently no AI-outage failure mode to degrade from at all: the deterministic pace engine, snapshotting, and dashboard all function independently of any third-party AI availability.

**5. AI Assistance & Provenance**

------------------------------------------------------------------------

We used Claude to help run and interpret the Semgrep scan, trace ownership checks through the codebase, and research the httpx2 dependency. All findings were verified against the actual repository (github.com/NatiSeifu/goal-wise) rather than described hypothetically — the Semgrep results, file paths, and line numbers in this report come from a real scan, not a generated example. The team reviewed every finding, made the triage calls, and owns the security decisions in this report.

*References: OWASP Foundation, “Cross Site Request Forgery (CSRF),” https://owasp.org/www-community/attacks/csrf; OWASP Foundation, “SQL Injection,” https://owasp.org/www-community/attacks/SQL_Injection; Semgrep official rules, https://github.com/semgrep/semgrep-rules*
