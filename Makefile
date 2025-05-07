# Makefile for Palo Alto Networks MCP Server
# ------------------------------------------------------------------------------------
# This Makefile provides commands for development, testing, and deployment.
# Run `make help` to see a list of available commands.

# Variables
# ------------------------------------------------------------------------------------
DOCKER_COMPOSE = docker compose -f infrastructure/compose/docker-compose.yml
PACKAGE_DIR = src
TEST_DIR = tests
PYTHON = python
POETRY = poetry
UV = uv
VENV_DIR = .venv
BLACK_OPTS = --line-length 100
ISORT_OPTS = --profile black
RUFF_OPTS = --fix
PYRIGHT_OPTS = 

# Docker commands
# ------------------------------------------------------------------------------------
.PHONY: build up down logs restart

## Build Docker containers
build:
	@echo "Building Docker containers..."
	$(DOCKER_COMPOSE) build

## Start Docker containers in detached mode
up:
	@echo "Starting Docker containers..."
	$(DOCKER_COMPOSE) up -d

## Stop and remove Docker containers
down:
	@echo "Stopping Docker containers..."
	$(DOCKER_COMPOSE) down

## Show logs from Docker containers
logs:
	@echo "Showing logs from Docker containers..."
	$(DOCKER_COMPOSE) logs -f

## Restart Docker containers
restart: down up

# Code Quality
# ------------------------------------------------------------------------------------
.PHONY: lint format typecheck pre-commit install-pre-commit clean-pyc

## Run all linting checks
lint: lint-isort lint-ruff lint-format-check lint-flake8

## Check imports with isort
lint-isort:
	@echo "Checking imports with isort..."
	$(POETRY) run isort --check-only $(ISORT_OPTS) $(PACKAGE_DIR) $(TEST_DIR)

## Check code with ruff
lint-ruff:
	@echo "Checking code with ruff..."
	$(POETRY) run ruff check $(PACKAGE_DIR) $(TEST_DIR)

## Check formatting with ruff
lint-format-check:
	@echo "Checking formatting with ruff..."
	$(POETRY) run ruff format --check $(PACKAGE_DIR) $(TEST_DIR)

## Check code with flake8
lint-flake8:
	@echo "Checking code with flake8..."
	$(POETRY) run flake8 $(PACKAGE_DIR) $(TEST_DIR)

## Format code with isort and ruff
format:
	@echo "Formatting imports with isort..."
	$(POETRY) run isort $(ISORT_OPTS) $(PACKAGE_DIR) $(TEST_DIR)
	@echo "Formatting code with ruff..."
	$(POETRY) run ruff format $(PACKAGE_DIR) $(TEST_DIR)

## Run type checking with mypy and pyright
typecheck: typecheck-mypy typecheck-pyright

## Check types with mypy
typecheck-mypy:
	@echo "Type checking with mypy..."
	$(POETRY) run mypy $(PACKAGE_DIR)

## Check types with pyright
typecheck-pyright:
	@echo "Type checking with pyright..."
	$(POETRY) run pyright $(PACKAGE_DIR)

## Run pre-commit hooks on all files
pre-commit:
	@echo "Running pre-commit hooks..."
	$(POETRY) run pre-commit run --all-files

## Install pre-commit hooks
install-pre-commit:
	@echo "Installing pre-commit hooks..."
	$(POETRY) run pip install pre-commit
	pre-commit install

## Clean Python cache files
clean-pyc:
	@echo "Cleaning Python cache files..."
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '__pycache__' -delete
	find . -name '.ruff_cache' -delete
	find . -name '.mypy_cache' -delete
	find . -name '.pytest_cache' -delete

# Development and Testing
# ------------------------------------------------------------------------------------
.PHONY: install run test coverage

## Install the package in development mode
install:
	@echo "Installing package in development mode..."
	$(POETRY) install --with dev

## Install the package using uv
install-uv:
	@echo "Installing package using uv..."
	$(UV) pip install -e ".[dev]"

## Run the MCP server
run:
	@echo "Running MCP server..."
	$(PYTHON) -m palo_alto_mcp

## Run tests with pytest
test:
	@echo "Running tests..."
	$(POETRY) run pytest $(TEST_DIR)

## Run tests with coverage report
coverage:
	@echo "Running tests with coverage..."
	$(POETRY) run pytest --cov=$(PACKAGE_DIR) --cov-report=term-missing $(TEST_DIR)

# Package Management
# ------------------------------------------------------------------------------------
.PHONY: build-package publish-package

## Build package for distribution
build-package:
	@echo "Building package for distribution..."
	$(POETRY) build

## Publish package to PyPI
publish-package:
	@echo "Publishing package to PyPI..."
	$(POETRY) publish

# Help
# ------------------------------------------------------------------------------------
.PHONY: help

## Show this help message
help:
	@echo "Palo Alto Networks MCP Server Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^## [a-zA-Z_-]+:' $(MAKEFILE_LIST) | sed 's/## //' | column -t -s ':'