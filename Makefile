.PHONY: backend-sync backend-format backend-lint backend-typecheck backend-test backend-check backend-migrate backend-migration-current backend-migration-downgrade check

UV ?= uv
BACKEND_PROJECT ?= backend
BACKEND_UV_ENV ?= ../.venv

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

check: backend-check
