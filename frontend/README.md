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
