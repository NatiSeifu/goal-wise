# GoalWise Backend

Backend Python tooling is configured in `pyproject.toml`.

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
