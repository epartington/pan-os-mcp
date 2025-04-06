#!/bin/bash
# Script to run code quality checks locally
# Similar to the GitHub Actions workflow

set -e  # Exit on error

echo "Running code quality checks..."

# Run isort
echo "Running isort..."
poetry run isort --check-only --profile black src tests || { echo "isort check failed"; exit 1; }

# Run ruff lint
echo "Running ruff lint..."
poetry run ruff check src tests || { echo "ruff lint failed"; exit 1; }

# Run ruff format
echo "Running ruff format check..."
poetry run ruff format --check src tests || { echo "ruff format check failed"; exit 1; }

# Run flake8
echo "Running flake8..."
poetry run flake8 src tests || { echo "flake8 check failed"; exit 1; }

# Run mypy
echo "Running mypy type checking..."
poetry run mypy src || { echo "mypy check failed"; exit 1; }

# Run pyright
echo "Running pyright type checking..."
poetry run pyright src || { echo "pyright check failed"; exit 1; }

# Run yamllint (only on docs, scripts, src, tests and mkdocs.yml)
echo "Running YAML linting..."
poetry run yamllint -c .yamllint docs/ scripts/ src/ tests/ mkdocs.yml || { echo "YAML linting failed"; exit 1; }

# Fix docstring issues automatically and then check
echo "Fixing docstring issues..."
poetry run ruff check --select D --fix src tests

# Check for security issues (ignoring specific known issues)
echo "Checking for security issues..."
poetry run ruff check --select S --ignore S501,S314 src tests || { echo "Security check failed"; exit 1; }

# Check for unused imports
echo "Checking for unused imports..."
poetry run ruff check --select F401 src tests || { echo "Unused imports check failed"; exit 1; }

# Check for undefined names
echo "Checking for undefined names..."
poetry run ruff check --select F821 src tests || { echo "Undefined names check failed"; exit 1; }

# Validate mkdocs configuration
echo "Validating mkdocs configuration..."
poetry run mkdocs build --strict --site-dir /tmp/mkdocs-build || { echo "MkDocs validation failed"; exit 1; }

echo "All code quality checks passed!"
