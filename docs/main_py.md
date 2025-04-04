# main.py Documentation

This document provides a line-by-line explanation of the `main.py` module, which serves as the entry point and core server component of the PAN-OS MCP server.

## File Purpose

`main.py` initializes and runs the MCP server with SSE transport. It:
- Configures the server and its endpoints
- Sets up logging
- Creates the server instance
- Registers tool handlers
- Manages SSE connections
- Handles routing and health checks

## Import Statements

```python
import logging
import os
import uuid

import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from tools import register_tools
```

### Import Details

- **Standard Library Imports**:
  - `logging`: For structured logging throughout the application
  - `os`: To access environment variables like PORT and DEBUG settings
  - `uuid`: To generate unique request identifiers for logging

- **Framework Imports**:
  - `uvicorn`: ASGI web server implementation for running the application
  - `mcp.server.Server`: The core MCP server class from the MCP Python SDK
  - `mcp.server.sse.SseServerTransport`: SSE transport implementation from the MCP SDK
  - `starlette.applications.Starlette`: Web framework for creating the HTTP application
  - `starlette.responses.JSONResponse`: For returning JSON responses (health checks)
  - `starlette.routing.Mount, Route`: For defining HTTP routes

- **Local Imports**:
  - `tools.register_tools`: Function to register MCP tools with the server

## Logging Configuration

```python
logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mcp-paloalto")
logger.setLevel(logging.DEBUG)
```

- Sets up structured logging with timestamp, logger name, level, and message
- Uses DEBUG level if the DEBUG environment variable is set, otherwise INFO
- Creates a logger instance with the name "mcp-paloalto"
- Sets the logger level to DEBUG for detailed logging

## Main Server Function

```python
def run_server():
    """
    Start the MCP server with SSE transport.
    """
    # Initialize the MCP server
    mcp_server = Server("panos-mcp")

    # Register tool handlers
    register_tools(mcp_server)

    # Create SSE transport
    sse_transport = SseServerTransport("/messages/")
    logger.debug("Created SSE transport")
```

- Creates an instance of the MCP Server with name "panos-mcp"
- Registers all tool handlers defined in the tools.py module
- Creates an SSE transport with the endpoint path "/messages/"
- The trailing slash in "/messages/" is critical for proper routing

## SSE Handler

```python
async def handle_sse(request):
    """Handle an SSE connection request."""
    logger.debug(f"SSE request details: {request.url.path}, {dict(request.query_params)}")
    client = request.scope.get("client", ("unknown", 0))
    logger.info(f"New MCP SSE connection from {client[0]}:{client[1]}")

    try:
        # This follows exactly the SDK example pattern
        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
            logger.info("SSE session established")
            await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())
    except Exception as e:
        logger.exception(f"Error in SSE handler: {str(e)}")
        return JSONResponse({"error": "Connection error"}, status_code=500)
```

- Handles incoming SSE connection requests at the "/sse" endpoint
- Logs details about the connection including client IP and port
- Creates an SSE connection using the transport's connect_sse method
- The connection provides two streams for bidirectional communication
- Runs the MCP server with these streams and default initialization options
- Catches and logs any exceptions that occur during the connection

## Health Check Endpoint

```python
async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({"status": "OK"})
```

- Simple health check handler that returns a JSON response with status "OK"
- Used for liveness and readiness probes in Kubernetes deployments

## Routing Configuration

```python
routes = [
    Route("/", endpoint=health_check),
    Route("/health", endpoint=health_check),
    Route("/readiness", endpoint=health_check),
    Route("/liveness", endpoint=health_check),
    Route("/sse", endpoint=handle_sse),
    Mount("/messages", app=sse_transport.handle_post_message),
]
```

- Defines all HTTP routes for the application:
  - `/`, `/health`, `/readiness`, `/liveness`: All map to the health check handler
  - `/sse`: The SSE connection endpoint
  - `/messages`: Mounted to the SSE transport's message handling function
- The order of routes is important for proper routing

## Starlette App Creation and Server Startup

```python
app = Starlette(debug=True, routes=routes)

# Log information about configured routes
logger.info(f"Configured routes: {[route.path for route in routes]}")
logger.info("Server configured with SSE endpoint at: /sse")
logger.info("Health check available at: /health")

# Run the server
port = int(os.environ.get("PORT", 8001))
logger.info({"request_id": str(uuid.uuid4()), "message": "MCP server starting up"})
uvicorn.run(app, host="0.0.0.0", port=port)
```

- Creates a Starlette app with debug mode enabled and the defined routes
- Logs information about the configured routes for easier debugging
- Determines the port to run on from the PORT environment variable or defaults to 8001
- Logs a server startup message with a unique request ID
- Starts the Uvicorn server with the Starlette app

## Entry Point

```python
if __name__ == "__main__":
    run_server()
```

- Standard Python idiom to run the server when the file is executed directly
- Calls the run_server function to start the MCP server
