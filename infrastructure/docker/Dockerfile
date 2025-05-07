# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and install dependencies first for caching
COPY pyproject.toml ./pyproject.toml
COPY poetry.toml ./poetry.toml
COPY README.md ./README.md

# Install Poetry (if needed) or use pip
RUN pip install --upgrade pip && pip install poetry
RUN poetry install --no-interaction --no-root

# Copy the rest of the codebase
COPY src ./src

# Set PYTHONPATH so src is importable
ENV PYTHONPATH=/app/src

# Expose port for FastMCP HTTP/SSE server
EXPOSE 8000

# Entrypoint: run the server
CMD ["python", "-m", "palo_alto_mcp"]
