.PHONY: help venv install run dev test lint fmt clean

PYTHON := python3.12
VENV := .venv
VENV_BIN := $(VENV)/bin

help:
	@echo "Hurl - Makefile commands"
	@echo ""
	@echo "  make venv      - Create virtual environment"
	@echo "  make install   - Install dependencies"
	@echo "  make run       - Run production server"
	@echo "  make dev       - Run development server with reload"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linters"
	@echo "  make fmt       - Format code"
	@echo "  make clean     - Clean temporary files"

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created. Activate with: source $(VENV_BIN)/activate"

install: venv
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r requirements.txt
	@echo "Dependencies installed"

install-dev: install
	$(VENV_BIN)/pip install -e ".[dev]"
	@echo "Development dependencies installed"

run:
	$(VENV_BIN)/python -m backend.app.main

dev:
	$(VENV_BIN)/uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(VENV_BIN)/pytest tests/ -v --cov=backend --cov-report=html

test-fast:
	$(VENV_BIN)/pytest tests/ -v

lint:
	$(VENV_BIN)/ruff check backend/
	$(VENV_BIN)/mypy backend/

fmt:
	$(VENV_BIN)/black backend/
	$(VENV_BIN)/ruff check --fix backend/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage
	@echo "Cleaned temporary files"

hurlgen:
	$(VENV_BIN)/python backend/scripts/hurlgen.py $(ARGS)
