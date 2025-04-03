# To-Do List: MCP Palo Alto Integration Server

## 1. Project Setup

- [ ] Create a new project directory: `mcp-paloalto`
- [ ] Initialize a Git repository in the project directory
- [ ] Set up a virtual environment for Python 3.11
- [ ] Create a `requirements.txt` file with dependencies:
  - fastapi
  - uvicorn
  - aiohttp
  - pydantic
- [ ] Install dependencies using `pip install -r requirements.txt`

## 2. Application Development

### 2.1 Directory Structure

- [ ] Create `src/` directory
- [ ] Create subdirectories: `src/models/`, `src/services/`, `src/tools/`
- [ ] Create empty files:
  - `src/main.py`
  - `src/models/palo_alto.py`
  - `src/services/palo_alto_api.py`
  - `src/tools/palo_alto_tools.py`

### 2.2 FastAPI Application

- [ ] Implement FastAPI app initialization in `src/main.py`
- [ ] Define MCP request model using Pydantic in `src/main.py`
- [ ] Add `/mcp/tools` GET endpoint to return available tools
- [ ] Add `/mcp/execute` POST endpoint to handle tool execution
- [ ] Implement error handling for invalid tools and API failures

### 2.3 Palo Alto API Integration

- [ ] Create `PaloAltoAPI` class in `src/services/palo_alto_api.py`
- [ ] Implement async HTTP client initialization using `aiohttp`
- [ ] Add `_make_request` helper method for API calls
- [ ] Implement `get_address_objects` method with XML API xpath
- [ ] Implement `get_security_zones` method with XML API xpath
- [ ] Implement `get_security_policies` method with XML API xpath

### 2.4 MCP Tools Definition

- [ ] Define `palo_alto_tools` list in `src/tools/palo_alto_tools.py`
- [ ] Add tool definition for `retrieve_address_objects`
- [ ] Add tool definition for `retrieve_security_zones`
- [ ] Add tool definition for `retrieve_security_policies`

## 3. Containerization

- [ ] Create `Dockerfile` in project root
- [ ] Configure Dockerfile to:
  - Use `python:3.11-slim` base image
  - Set working directory to `/app`
  - Copy and install requirements
  - Copy `src/` directory
  - Run `uvicorn` on port 8000
- [ ] Build Docker image locally to verify

## 4. Kubernetes Setup

### 4.1 Namespace and Base Configuration

- [ ] Create `kubernetes/` directory
- [ ] Create `namespace.yaml` for `mcp-paloalto` namespace
- [ ] Create `deployment.yaml` for FastAPI application
- [ ] Configure deployment with:
  - 2 replicas
  - Container port 8000
  - Environment variables for Palo Alto hostname and API key
  - Secret reference for API key

### 4.2 Metallb Configuration

- [ ] Create `metallb-config.yaml` in `kubernetes/`
- [ ] Define IP address pool (e.g., 192.168.1.100-192.168.1.150)

### 4.3 Traefik Configuration

- [ ] Create `traefik-deployment.yaml` in `kubernetes/`
- [ ] Configure Traefik with:
  - Port 443 exposure
  - Kubernetes CRD provider
  - Web entrypoint
- [ ] Create `ingressroute.yaml` in `kubernetes/`
- [ ] Configure IngressRoute to:
  - Match host `mcp.paloalto.local`
  - Route to FastAPI service on port 8000
  - Enable TLS termination

## 5. Security Implementation

- [ ] Create Kubernetes Secret manifest for Palo Alto API key
- [ ] Add input validation to FastAPI endpoints
- [ ] Configure Traefik for TLS termination

## 6. Testing

- [ ] Test `/mcp/tools` endpoint locally with `curl` or Postman
- [ ] Test `/mcp/execute` endpoint with each tool and valid parameters
- [ ] Verify error handling with invalid tool names and parameters
- [ ] Test Docker container locally with sample API key
- [ ] Deploy to a local Kubernetes cluster (e.g., Minikube) and verify connectivity

## 7. Monitoring and Logging

- [ ] Add basic logging to FastAPI application
- [ ] Implement health check endpoint (e.g., `/health`)
- [ ] Configure Kubernetes liveness and readiness probes in `deployment.yaml`

## 8. Documentation

- [ ] Update README.md with:
  - Project overview
  - Setup instructions
  - Deployment steps
  - Example API calls
- [ ] Document environment variables required
- [ ] Add usage examples for Windsurf client

## 9. Deployment Preparation

- [ ] Tag Docker image for production registry
- [ ] Push Docker image to container registry
- [ ] Prepare Kubernetes manifests for production cluster
- [ ] Verify Metallb and Traefik configurations match production network

## 10. Final Validation

- [ ] Deploy to production Kubernetes cluster
- [ ] Verify Traefik routes traffic correctly
- [ ] Test end-to-end functionality with Windsurf client
- [ ] Confirm TLS termination works as expected
