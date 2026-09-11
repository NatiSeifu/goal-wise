# GoalWise Frontend

React + Vite frontend code lives under `src/`.

Install dependencies from the repository root:

```sh
make frontend-sync
```

Run the local dev server:

```sh
make frontend-dev
```

Run frontend checks:

```sh
make frontend-check
```

Configure the backend origin for local API calls with:

```sh
cp frontend/.env.example frontend/.env
```

For local development, `VITE_API_BASE_URL` should point at the FastAPI backend,
such as `http://localhost:8000`. The dev server uses `http://localhost:5173` to
match the backend CORS default.

For hosted Railway deployments, leave `VITE_API_BASE_URL` unset or empty so the
React app calls same-origin `/api/*` paths. The frontend Caddy container proxies
those requests to `API_PROXY_TARGET`.

The frontend may format backend-provided values for display, but it must not
duplicate the backend `pace-v1` calculation formulas or official dashboard
metric logic.

## UI verification

Content and hierarchy follow [SPEC-0012](../docs/specs/0012-ui-content-and-hierarchy.md).
Run `npm run visual` with the local frontend running to capture all eight routes
plus the generated dashboard digest at desktop, tablet, and mobile sizes. The capture uses fixed synthetic backend
responses from `scripts/ui-fixture.json` and an accepted provider response for
those synthetic At Risk metrics in `scripts/ai-digest-at-risk-fixture.json`.
The digest capture explicitly clicks Generate digest and shows the returned
overview, observations, trusted metric references, and review-goal action.
No deferred actions are represented. The capture does not create accounts or modify
backend data. PNGs go to `/tmp/goal-wise-ui`. Override `PLAYWRIGHT_BASE_URL` or
`VISUAL_OUTPUT_DIR` when needed.
