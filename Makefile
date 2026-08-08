.PHONY: backend-sync backend-format backend-lint backend-typecheck backend-test backend-check backend-migrate backend-migration-current backend-migration-downgrade backend-db-up backend-db-down backend-db-logs backend-stack-up backend-stack-down backend-stack-logs backend-image-build backend-image-run check

UV ?= uv
BACKEND_PROJECT ?= backend
BACKEND_UV_ENV ?= ../.venv
BACKEND_IMAGE ?= goalwise-backend:local

backend-sync:
	cd $(BACKEND_PROJECT) && UV_PROJECT_ENVIRONMENT=$(BACKEND_UV_ENV) $(UV) sync --extra dev

backend-format:
	cd $(BACKEND_PROJECT) && UV_PROJECT_ENVIRONMENT=$(BACKEND_UV_ENV) $(UV) run ruff format app tests

backend-lint:
	cd $(BACKEND_PROJECT) && UV_PROJECT_ENVIRONMENT=$(BACKEND_UV_ENV) $(UV) run ruff check app tests

backend-typecheck:
	cd $(BACKEND_PROJECT) && UV_PROJECT_ENVIRONMENT=$(BACKEND_UV_ENV) $(UV) run mypy

backend-test:
	cd $(BACKEND_PROJECT) && UV_PROJECT_ENVIRONMENT=$(BACKEND_UV_ENV) $(UV) run pytest

backend-check: backend-lint backend-typecheck backend-test

backend-migrate:
	cd $(BACKEND_PROJECT) && UV_PROJECT_ENVIRONMENT=$(BACKEND_UV_ENV) $(UV) run alembic upgrade head

backend-migration-current:
	cd $(BACKEND_PROJECT) && UV_PROJECT_ENVIRONMENT=$(BACKEND_UV_ENV) $(UV) run alembic current

backend-migration-downgrade:
	cd $(BACKEND_PROJECT) && UV_PROJECT_ENVIRONMENT=$(BACKEND_UV_ENV) $(UV) run alembic downgrade -1

backend-db-up:
	docker compose up -d postgres

backend-db-down:
	docker compose down

backend-db-logs:
	docker compose logs -f postgres

backend-stack-up:
	docker compose up -d postgres backend

backend-stack-down:
	docker compose down

backend-stack-logs:
	docker compose logs -f backend postgres

backend-image-build:
	docker build --target production -t $(BACKEND_IMAGE) $(BACKEND_PROJECT)

backend-image-run:
	docker run --rm -p 8000:8000 $(BACKEND_IMAGE)

check: backend-check
