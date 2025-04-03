# Use Python 3.12 slim as the base image
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set working directory
WORKDIR /app

# Copy only the files needed for installing dependencies
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --without dev --no-root

# Copy the rest of the application
COPY src ./src

# Lightweight runtime stage
FROM python:3.12-slim AS runtime

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app \
    PATH="/usr/local/bin:$PATH"

# Copy installed packages and application from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Make port 80 available
EXPOSE 80

# Define health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Run the application
CMD ["uvicorn", "src.panos_mcp.main:app", "--host", "0.0.0.0", "--port", "80"]
