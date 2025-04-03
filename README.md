# PAN-OS MCP Server

This repository contains the source code and deployment manifests for the PAN-OS MCP (Management Control Plane) server.

## Overview

The MCP server is a FastAPI application designed to interact with Palo Alto Networks NGFWs via an XML API, providing a consistent interface for retrieving firewall configuration data.

## Technology Stack

- **Application Framework:** FastAPI
- **Dependency Management:** Poetry
- **Containerization:** Docker (multi-architecture build)
- **Orchestration:** Kubernetes
- **Load Balancing:** MetalLB (Layer 2 mode)
- **Ingress Controller:** Traefik (with TLS termination)
- **Code Quality:** Flake8 (linting), Ruff (formatting)
- **XML Parsing:** xmltodict

## Project Structure

```text
.
├── docker/              # Docker-related files
│   └── Dockerfile       # Multi-stage, multi-arch Dockerfile
├── k8s/                 # Kubernetes manifests
│   ├── deployment.yaml  # Deployment configuration
│   ├── ingress.yaml     # Ingress configuration
│   └── service.yaml     # Service configuration
├── src/                 # Application source code
│   └── panos_mcp/       # Python package
│       ├── __init__.py
│       ├── __main__.py  # Entry point
│       ├── config.py    # Configuration settings
│       └── main.py      # FastAPI application
├── Makefile             # Development and deployment tasks
├── poetry.toml          # Poetry local configuration
└── pyproject.toml       # Project dependencies and metadata
```

## Development

### Setup

1. **Install Poetry:**

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies:**

   ```bash
   poetry install
   ```

3. **Run the server locally:**

   ```bash
   poetry run python -m src.panos_mcp
   ```

Or using the Makefile:

   ```bash
   make run
   ```

### Code Quality

- **Linting:**

  ```bash
  make lint
  ```

- **Formatting:**

  ```bash
  make format
  ```

## Deployment

### Building and Pushing Docker Image

1. **Build multi-architecture Docker image:**

   ```bash
   make build
   ```

2. **Push to Docker registry:**

   ```bash
   make push
   ```

### Kubernetes Deployment

1. **Update Kubernetes Manifests:**
   - Ensure the image path in `k8s/deployment.yaml` points to your registry.
   - Replace `mcp.cdot.io` in `k8s/ingress.yaml` with your actual domain.

2. **Create TLS Secret:**
   Create a Kubernetes secret named `panos-mcp-tls` containing your TLS certificate and key.

   ```bash
   kubectl create secret tls panos-mcp-tls --cert=path/to/tls.crt --key=path/to/tls.key -n panos
   ```

3. **Apply Manifests:**

   ```bash
   make deploy
   ```

Or manually:

   ```bash
   kubectl apply -f k8s/
   ```

## API Endpoints

- `/` - Root endpoint with welcome message
- `/health` - Health check endpoint
- `/mcp/tools` - List available tools and their parameters
- `/mcp/execute` - Execute a tool with specific parameters (POST)

## Environment Variables

- `PANOS_API_KEY` - API Key for authenticating with Palo Alto Networks firewalls
- `PANOS_HOSTNAME` - Hostname of the target firewall
- `LOG_LEVEL` - Logging level (default: "info")
