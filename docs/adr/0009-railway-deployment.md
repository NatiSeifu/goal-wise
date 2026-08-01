# ADR-0009: Deploy the Course MVP on Railway

- **Status:** Accepted
- **Date:** 2026-08-01
- **Deciders:** Nati Seifu
- **Related requirements:** NFR-SEC-002, NFR-SEC-004, NFR-SEC-007, NFR-REL-002, NFR-MNT-001, Software Interfaces 4.3.2, Communication Interfaces 4.3.3

## Context

GoalWise needs a hosted course/demo deployment for a React + Vite frontend, FastAPI backend, and PostgreSQL database. The deployment target must support environment variables, public service domains, managed PostgreSQL, and a straightforward path for static frontend hosting.

Deployment affects cookie settings, CORS, CSRF, migrations, and whether the frontend/backend can be treated as same-site.

## Decision

We will use Railway for the course MVP deployment.

Deployment shape:

- React + Vite frontend deployed as a Railway static site or static frontend service.
- FastAPI backend deployed as a Railway web service.
- PostgreSQL provisioned through Railway PostgreSQL.
- Runtime configuration supplied through Railway service variables.
- Railway-provided domains are acceptable for course demo; custom same-site subdomains are preferred if available.

```mermaid
flowchart LR
    User[Browser] --> Frontend[Railway Frontend Service]
    Frontend -->|JSON /api/v1 with credentials| API[Railway FastAPI Service]
    API --> DB[(Railway PostgreSQL)]
    API --> Vars[Railway Service Variables]
```

## Alternatives considered

- **Railway** - Chosen because it has good prototype ergonomics, managed PostgreSQL, service variables, public domains, static hosting support, and simple GitHub-driven deployment. Pricing and usage must be monitored.
- **Render** - Rejected because it has a similar static site, web service, and PostgreSQL story, but the team prefers Railway's workflow.
- **Fly.io** - Rejected because it requires more Docker and operations comfort than the MVP needs.
- **Vercel frontend plus separate backend host** - Rejected because cross-site API cookies and CORS become more complex.
- **Local/demo only** - Rejected because it is not enough for a reachable course demo deployment.

## Consequences

**Positive:**

- One platform can host frontend, backend, and database.
- Railway service variables can hold database URL, session secret, cookie settings, and allowed frontend origin.
- Railway PostgreSQL aligns with the hosted PostgreSQL requirement.
- Railway public domains allow quick demo deployment.

**Negative:**

- If frontend and backend use unrelated Railway-provided domains, cookie behavior may require cross-site settings.
- Usage limits and billing must be monitored.
- Same-site cookie simplicity may require custom domains.

**Neutral / follow-ups:**

- Frontend deploys and can reach the backend over the configured public API origin.
- Backend reads `DATABASE_URL` and connects to Railway PostgreSQL.
- Alembic migrations run against Railway PostgreSQL before demo use.
- Hosted cookies use `Secure=true`.
- Same-site deployments use `SameSite=Lax`; cross-site deployments use `SameSite=None`, `Secure=true`, explicit CORS allowlist, credentials, and CSRF verification.
- Health check endpoint verifies API availability for the demo window.

## AI assistance & provenance

AI helped compare deployment platform alternatives and identify cookie, CORS, CSRF, and database implications. The project owner chose Railway based on MVP deployment ergonomics and preference after discussing alternatives. We verified the decision against the SRS hosted-environment and communication requirements by documenting Railway service variables, PostgreSQL use, HTTPS expectations, and cookie policy follow-ups.
