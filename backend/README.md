# GoalWise Backend

Backend Python tooling is configured in `pyproject.toml`.

Runtime configuration is environment-driven. Local `.env` files are supported for
developer convenience, but they are ignored by git and tests force their own safe
settings.

Create the project virtual environment and install development dependencies from the
repository root:

```sh
uv venv
make backend-sync
```

Common commands from the repository root:

```sh
make backend-format
make backend-lint
make backend-typecheck
make backend-test
make backend-check
make backend-migrate
make backend-migration-current
```

The root `Makefile` runs backend tools through `uv` from the backend directory while
pointing uv at the repository-root `.venv`, so checks use the project environment
instead of the global Python installation.

## Environment Variables

Use `backend/.env.example` as the local template:

```text
ENVIRONMENT=local
DATABASE_URL=postgresql+psycopg://goalwise:goalwise_dev_password@localhost:5432/goalwise_dev
SESSION_SECRET=local-dev-session-secret-change-me
SECURE_COOKIES=false
COOKIE_SAMESITE=lax
ALLOWED_FRONTEND_ORIGIN=http://localhost:5173
```

Production or hosted environments must provide real secret values through the host
environment, not committed files. In production, `SESSION_SECRET` must be changed
from the local default and `SECURE_COOKIES` must be enabled.

## Local PostgreSQL

The deploy-readiness path uses Docker Compose for a local PostgreSQL database while
the FastAPI backend still runs from the host through `uv`.

Start the database:

```sh
make backend-db-up
```

Copy `backend/.env.example` to `backend/.env` if you want the backend and Alembic
commands to use the local PostgreSQL database by default. Then run migrations:

```sh
make backend-migrate
make backend-migration-current
```

Run the backend from the repository root:

```sh
cd backend
UV_PROJECT_ENVIRONMENT=../.venv uv run uvicorn app.main:app --reload
```

Check runtime readiness:

```sh
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Run the production backend image with the Compose database:

```sh
make backend-stack-up
curl http://localhost:8000/health
curl http://localhost:8000/ready
make backend-stack-down
```

If port `8000` is already in use, override the host port:

```sh
BACKEND_PORT=18000 make backend-stack-up
curl http://localhost:18000/health
```

Inside Docker Compose, the backend connects to PostgreSQL through the service name
`postgres`. From your host machine, use `localhost` or `127.0.0.1` in
`DATABASE_URL`.

## Migrations

Alembic migrations run against the configured `DATABASE_URL`:

```sh
make backend-migrate
make backend-migration-current
make backend-migration-downgrade
```

Run migrations before using a new database and after pulling schema changes. The
CI workflow also runs a PostgreSQL migration smoke check against a temporary
database service.

## Browser Runtime Settings

The backend allows credentialed browser requests from `ALLOWED_FRONTEND_ORIGIN`.
For local React development, the default is:

```text
ALLOWED_FRONTEND_ORIGIN=http://localhost:5173
```

The frontend must call the API with credentials enabled so the HTTP-only session
cookie is included. Unsafe authenticated requests must also send `X-CSRF-Token`.

Stop the database:

```sh
make backend-db-down
```

## CI

Backend CI runs on pull requests to `development` when backend, Compose, Makefile,
or workflow files change. It installs dependencies with `uv`, runs linting,
typechecking, tests, a PostgreSQL migration smoke check, and builds the backend
Docker image.

The CI database is temporary and does not require project secrets.

## Railway Notes

Railway deployment is deferred. When deployment starts, Railway should provide:

- `DATABASE_URL` from the Railway PostgreSQL service.
- `ENVIRONMENT=production`.
- A generated `SESSION_SECRET`.
- `SECURE_COOKIES=true`.
- `COOKIE_SAMESITE=none` if the frontend and backend are cross-site.
- An explicit `ALLOWED_FRONTEND_ORIGIN` for the deployed frontend URL.

Run Alembic migrations as an explicit deploy or release step before routing demo
traffic to a new schema.
