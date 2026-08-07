.PHONY: backend-format backend-lint backend-typecheck backend-test backend-check check

PYTHON ?= python3

backend-format:
	cd backend && $(PYTHON) -m ruff format app tests

backend-lint:
	cd backend && $(PYTHON) -m ruff check app tests

backend-typecheck:
	cd backend && $(PYTHON) -m mypy

backend-test:
	cd backend && $(PYTHON) -m pytest

backend-check: backend-lint backend-typecheck backend-test

check: backend-check
