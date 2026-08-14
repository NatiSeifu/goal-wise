.PHONY: dev-sync dev-up dev-down dev-destroy dev-logs dev-status seed-user-stories backend-sync backend-format backend-lint backend-typecheck backend-test backend-check backend-migrate backend-compose-migrate backend-migration-current backend-migration-downgrade backend-db-up backend-db-down backend-db-logs backend-stack-up backend-stack-down backend-stack-logs backend-image-build backend-image-run frontend-sync frontend-dev frontend-build frontend-lint frontend-test frontend-check check

UV ?= uv
BACKEND_PROJECT ?= backend
BACKEND_UV_ENV ?= ../.venv
BACKEND_IMAGE ?= goalwise-backend:local
COMPOSE_DATABASE_URL ?= postgresql+psycopg://goalwise:goalwise_dev_password@localhost:5432/goalwise_dev
FRONTEND_PROJECT ?= frontend

dev-sync: backend-sync frontend-sync

dev-up:
	$(MAKE) backend-db-up
	$(MAKE) backend-compose-migrate
	$(MAKE) backend-stack-up
	$(MAKE) frontend-dev

dev-down: backend-stack-down

dev-destroy:
	@test "$(CONFIRM)" = "destroy" || (echo "This removes the local Postgres volume. Run CONFIRM=destroy make dev-destroy"; exit 1)
	docker compose down -v

dev-logs: backend-stack-logs

dev-status:
	docker compose ps

seed-user-stories:
	node scripts/seed-user-stories.mjs

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

backend-compose-migrate:
	cd $(BACKEND_PROJECT) && DATABASE_URL=$(COMPOSE_DATABASE_URL) UV_PROJECT_ENVIRONMENT=$(BACKEND_UV_ENV) $(UV) run alembic upgrade head

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

frontend-sync:
	cd $(FRONTEND_PROJECT) && npm ci

frontend-dev:
	cd $(FRONTEND_PROJECT) && npm run dev

frontend-build:
	cd $(FRONTEND_PROJECT) && npm run build

frontend-lint:
	cd $(FRONTEND_PROJECT) && npm run lint

frontend-test:
	cd $(FRONTEND_PROJECT) && npm run test

frontend-check: frontend-lint frontend-test frontend-build

check: backend-check frontend-check
