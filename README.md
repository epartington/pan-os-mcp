# PAN-OS MCP Server

This repository contains the implementation of an MCP (Model Context Protocol) server for Palo Alto Networks NGFW integration.

## Overview

The MCP server provides a standardized interface for retrieving configuration data from Palo Alto Networks Next-Generation Firewalls (NGFWs) using the MCP Python SDK. It allows clients to interact with PAN-OS devices through a consistent API surface.

## Technology Stack

- **MCP Framework:** [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- **Python Version:** 3.11
- **Network Communication:** async/await via `httpx` and `anyio`
- **Transport Protocol:** Server-Sent Events (SSE)
  - Initial connection via the `/sse` endpoint
  - Bidirectional communication via the `/messages/` endpoint
  - Automatic session ID generation and management via the MCP SDK
- **Authentication:** API key-based (environment variables)
- **Containerization:** Docker
- **Orchestration:** Kubernetes
- **CI/CD:** GitHub Actions

## Project Structure

```text
.
├── .github/             # GitHub configurations
│   ├── workflows/       # GitHub Actions workflows
│   └── branch-protection.json # Branch protection rules
├── kubernetes/          # Kubernetes manifests
│   └── deployment.yaml  # Deployment configuration
├── src/                 # Application source code
│   ├── main.py          # MCP server entry point
│   ├── tools.py         # Tools implementation
│   └── palo_alto_api.py # PAN-OS API integration
├── Dockerfile           # Docker build configuration
└── requirements.txt     # Project dependencies
```

## Features

The server exposes the following tools:

- **retrieve_address_objects**: Get address objects from the firewall
- **retrieve_security_zones**: Get security zones from the firewall
- **retrieve_security_policies**: Get security policies from the firewall

Each tool can be configured with:
- `location`: Location type (e.g., vsys, shared)
- `vsys`: VSYS identifier (default: vsys1)

## Development

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/cdot65/pan-os-mcp.git
   cd pan-os-mcp
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**

   ```bash
   export PANOS_API_KEY=your-api-key
   export PANOS_HOST=firewall-hostname-or-ip
   ```

4. **Run the server locally:**

   ```bash
   python src/main.py
   ```

### MCP Client Configuration

To connect to the server, configure your MCP client with:

```json
{
  "endpoint": "http://localhost:8001/sse",
  "messageEndpoint": "http://localhost:8001/messages/"
}
```

## API Endpoints

- `/sse` - SSE connection endpoint (establishes persistent connection with auto-generated session ID)
- `/messages/` - Message posting endpoint (requires session ID from SSE connection)
- `/health` - Health check endpoint
- `/readiness` - Readiness probe endpoint
- `/liveness` - Liveness probe endpoint

The endpoints follow the MCP SDK's prescribed pattern for session management:
1. Client establishes connection to `/sse`
2. Server assigns a session ID and sends it via the SSE stream
3. Client uses the session ID for all subsequent requests to `/messages/`

## Environment Variables

- `PANOS_API_KEY` - API Key for authenticating with Palo Alto Networks firewalls
- `PANOS_HOST` - Hostname or IP of the target firewall
- `LOG_LEVEL` - Logging level (default: "info")

## Deployment

### Docker

Build and run as a Docker container:

```bash
docker build -t pan-os-mcp .
docker run -p 8001:8001 -e PANOS_API_KEY=your-api-key -e PANOS_HOST=firewall-hostname pan-os-mcp
```

### Kubernetes

1. **Create a secret for API credentials:**

   ```bash
   kubectl create secret generic panos-credentials \
     --from-literal=api-key=your-api-key \
     --from-literal=host=firewall-hostname
   ```

2. **Deploy to Kubernetes:**

   ```bash
   kubectl apply -f kubernetes/deployment.yaml
   ```

## Contributing

Contributions are welcome! This repository uses branch protection rules to ensure code quality:

- Pull requests are required for changes to the main branch
- CI checks must pass before merging
- At least one approval is required for each PR

## License

This project is licensed under the MIT License - see the LICENSE file for details.
