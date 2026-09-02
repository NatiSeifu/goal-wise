# GoalWise 1.0.0 Production Readiness Rally

Status: Planning
Target: `v1.0.0`
Current baseline: `v0.3.0`

This rally turns the 1.0.0 release work into seven bounded workstreams. The
release means a supported, production-ready version of the current GoalWise
product, not implementation of every future SRS capability.

## Release Definition

GoalWise 1.0.0 is ready when the current planning workflow is reliable,
secure, understandable, observable, documented, and demonstrated end to end.
Deferred capabilities remain explicitly deferred unless product scope is
changed through the relevant SRS, spec, and ADR updates.

## Workstreams

### 1. Scope and acceptance baseline

**Status:** Not started

- Reconcile the README, product context, architecture, SRS traceability, and
  accepted specs with the shipped canonical planning CSV importer and runtime
  AI explanation layer.
- Decide which shipped capabilities are supported in 1.0 and which remain
  experimental or deferred.
- Turn the 1.0 acceptance criteria into a checklist with linked test evidence.
- Maintain a known-limitations list for one active goal, manual planning data,
  no bank sync, and no raw transaction import.

**Exit criteria:** The documentation describes the same product as the code,
and every 1.0 requirement has an owner, verification method, and disposition.

### 2. Correctness, ownership, and security

**Status:** In progress

- Add automated cross-user negative-authorization tests for every protected
  user-owned route, including reads and mutations.
- Cover goals, financial profile, income sources, planned expenses, dashboard,
  calculation snapshots, planning import preview/confirm, and AI explanations.
- For resource IDs owned by another user, assert `404`, no financial payload,
  and no state change. Include both API-level tests and service-level tests
  where ownership is enforced.
- Record the security review's `httpx2` conclusion: the package is real and is
  intentionally retained for the current test toolchain.
- Run SAST, dependency, secret, authorization, CSRF, cookie, CORS, and
  security-header checks against the release candidate.

**Exit criteria:** The security review's open items are closed or formally
accepted, with no unresolved Critical or High findings.

### 3. AI explanation hardening

**Status:** Needs verification

- Keep AI explain-only: it may describe a committed snapshot but cannot
  calculate, modify, or replace financial outputs.
- Verify disabled-provider, timeout, provider error, malformed response, and
  unavailable UI states.
- Ensure failures produce a clear retryable error state rather than a
  deterministic-looking fallback presented as an AI result.
- Test response-schema validation, privacy-minimized payloads, caching, and
  snapshot scoping.
- Add safe operational logging and confirm prompts, secrets, and financial
  payloads are not written to logs.

**Exit criteria:** AI failure is non-blocking to the financial product, and
all enabled/disabled/error paths have automated evidence.

### 4. Planning CSV import hardening

**Status:** Needs verification

- Test malformed CSV, missing headers, invalid values, duplicate rows,
  oversized files, excessive row counts, expired previews, cancellation, and
  confirmation failures.
- Verify preview data is isolated to the authenticated user.
- Verify confirmation is atomic and that persistence failure preserves the
  previously valid plan and snapshots.
- Add PostgreSQL migration and persistence coverage, not only SQLite coverage.
- Keep raw CSV content and unsupported transaction behavior out of snapshots.

**Exit criteria:** Import behavior is predictable, reversible on failure, and
covered in API, persistence, and browser tests.

### 5. Production deployment and operations

**Status:** Needs verification

- Run the Docker production build and startup path from a clean checkout.
- Verify required and optional environment variables, including behavior when
  `backend/.env` is absent.
- Rehearse PostgreSQL migrations, backup/restore, rollback, and health/readiness
  checks.
- Verify HTTPS, secure cookies, CSRF, CORS, rate limits, startup validation,
  and production logging.
- Define alertable signals for failed health checks, migration failures, and
  repeated API errors without logging sensitive values.

**Exit criteria:** A clean deployment can be performed from documented steps,
and rollback and recovery have been demonstrated.

### 6. UX, accessibility, and responsive quality

**Status:** Ongoing

- Freeze the information architecture before making further visual changes.
- Audit dashboard, financial inputs, planning import, calculation details, and
  all loading, empty, validation, error, and completed states.
- Check keyboard navigation, focus visibility, labels, contrast, semantics,
  mobile layout, text wrapping, and spacing at fixed desktop/mobile viewports.
- Use the Playwright visual capture utility after each meaningful UI change and
  inspect the rendered screenshots before committing.

**Exit criteria:** The primary workflow is usable by keyboard, readable on
  mobile and desktop, and has no known layout or copy defects in the release
  screenshots.

### 7. Release candidate and evidence package

**Status:** Not started

- Freeze feature work and create a release-candidate checklist.
- Run backend checks, frontend checks, full Playwright E2E, coverage, security,
  accessibility, performance, Docker, and PostgreSQL migration verification.
- Investigate and resolve any flaky or environment-sensitive E2E failures.
- Produce release notes, deployment guide, user guide, known-issues list,
  traceability updates, test reports, and security evidence.
- Open the `development -> main` release PR, merge it through review, then tag
  the merged `main` commit as `v1.0.0`.

**Exit criteria:** The release evidence package is complete and the release
  PR can be approved without relying on undocumented manual checks.

## Immediate Next Actions

1. Add the cross-user API test matrix and implement the missing cases.
2. Run the full backend and frontend E2E suites from a clean PostgreSQL-backed
   environment.
3. Reconcile the product and SRS documentation with the actual `v0.3.0`
   behavior.

## Explicitly Out of 1.0 Unless Re-scoped

- Multiple active goals.
- Bank synchronization.
- Raw bank-statement or transaction import.
- Transaction correction and duplicate handling.
- Background scheduling.
- Native mobile apps.
- Gamification.
