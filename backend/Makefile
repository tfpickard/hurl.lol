.PHONY: venv install run dev lint fmt test

VENV ?= .venv
PYTHON ?= python3

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV)/bin/pip install -U pip
	$(VENV)/bin/pip install -r requirements.txt

run:
	$(VENV)/bin/uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

dev: install run

lint:
	$(VENV)/bin/python -m compileall backend/app

fmt:
	@echo "Formatting handled via pre-commit (not implemented)."

test:
	$(VENV)/bin/pytest backend/tests
