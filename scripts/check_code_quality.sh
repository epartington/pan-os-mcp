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

echo "All code quality checks passed!"
