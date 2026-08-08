.PHONY: backend-sync backend-format backend-lint backend-typecheck backend-test backend-check check

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

check: backend-check
