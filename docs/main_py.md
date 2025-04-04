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
import json
import logging
import os
import traceback
import uuid
from dotenv import load_dotenv

import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from tools import register_tools
```

### Import Details

- **Standard Library Imports**:
  - `json`: For structured logging in JSON format
  - `logging`: For structured logging throughout the application
  - `os`: To access environment variables like PORT and DEBUG settings
  - `traceback`: For detailed error information in logs
  - `uuid`: To generate unique request identifiers for logging

- **External Imports**:
  - `dotenv.load_dotenv`: To load environment variables from .env file

- **Framework Imports**:
  - `uvicorn`: ASGI web server implementation for running the application
  - `mcp.server.Server`: The core MCP server class from the MCP Python SDK
  - `mcp.server.sse.SseServerTransport`: SSE transport implementation from the MCP SDK
  - `starlette.applications.Starlette`: Web framework for creating the HTTP application
  - `starlette.middleware.base.BaseHTTPMiddleware`: For custom middleware implementation
  - `starlette.requests.Request`: For handling HTTP requests
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

## Request Logging Middleware

```python
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):
        """Process the request and log both request and response details."""
        request_id = str(uuid.uuid4())
        client = request.scope.get("client", ("unknown", 0))
        logger.debug(
            json.dumps(
                {
                    "request_id": request_id,
                    "message": "Request received",
                    "path": request.url.path,
                    "method": request.method,
                    "client": f"{client[0]}:{client[1]}",
                    "query_params": str(dict(request.query_params)),
                }
            )
        )

        try:
            response = await call_next(request)
            logger.debug(
                json.dumps(
                    {
                        "request_id": request_id,
                        "message": "Response sent",
                        "status_code": response.status_code,
                    }
                )
            )
            return response
        except Exception as e:
            logger.error(
                json.dumps(
                    {
                        "request_id": request_id,
                        "message": f"Error processing request: {str(e)}",
                        "traceback": traceback.format_exc(),
                    }
                )
            )
            raise
```

- Creates a middleware that logs details about all HTTP requests and responses
- Generates a unique request ID for tracking the request through the logs
- Logs request details including path, method, client IP, and query parameters
- Logs response status code after request is handled
- Catches and logs any exceptions that occur during request handling

## Main Server Function

```python
def run_server():
    """
    Start the MCP server with SSE transport.
    """
    load_dotenv()  # Load environment variables

    # Create MCP server instance
    mcp_server = Server("panos-mcp")

    # Simple hooks for session lifecycle events
    async def on_session_start(session_id, transport_info):
        """Hook called when a new session starts."""
        logger.info(
            json.dumps(
                {
                    "message": "Session started",
                    "session_id": session_id,
                    "transport": transport_info,
                }
            )
        )

    async def on_session_end(session_id):
        """Hook called when a session ends."""
        logger.info(
            json.dumps(
                {
                    "message": "Session ended",
                    "session_id": session_id,
                }
            )
        )

    # Register session hooks with server
    mcp_server.on_session_start = on_session_start
    mcp_server.on_session_end = on_session_end

    # Register tool handlers
    register_tools(mcp_server)

    # Create SSE transport
    sse_transport = SseServerTransport("/messages/")
    logger.debug("Created SSE transport")
```

- Loads environment variables from .env file
- Creates an instance of the MCP Server with name "panos-mcp"
- Defines and registers session lifecycle hooks for logging
- Registers all tool handlers defined in the tools.py module
- Creates an SSE transport with the endpoint path "/messages/"
- The trailing slash in "/messages/" is critical for proper routing

## SSE Handler

```python
async def handle_sse(request):
    """Handle SSE connection from client."""
    client = f"{request.client[0]}:{request.client[1]}" if request.client else "unknown"
    logger.info(f"New MCP SSE connection from {client}")

    # Follow the exact pattern from the MCP SDK example
    async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
        logger.info("SSE session established")
        # Create initialization options
        init_options = mcp_server.create_initialization_options()
        # Run the MCP server with the streams
        await mcp_server.run(streams[0], streams[1], init_options)
```

- Handles SSE connection requests from MCP clients
- Logs the client IP address for connection tracking
- **Session Management**: Uses the MCP SDK's provided pattern for handling SSE connections
  - Delegates session ID generation to the SDK via `connect_sse`
  - Uses an async context manager to manage the connection lifecycle
  - The SDK automatically sends the session ID to the client via the SSE stream
- Creates initialization options and starts the MCP server with the connection streams
- No manual session tracking is necessary as the SDK handles this internally

## Message Handling Wrapper

```python
class DebugMessageHandling:
    """Wrapper around the SSE transport message handling to add debugging."""

    def __init__(self, original_app):
        self.app = original_app

    async def __call__(self, scope, receive, send):
        """ASGI application interface with added debugging."""
        request_id = str(uuid.uuid4())
        path = scope.get("path", "unknown")
        method = scope.get("method", "unknown")

        logger.debug(
            json.dumps(
                {
                    "request_id": request_id,
                    "message": "Message endpoint called",
                    "path": path,
                    "method": method,
                }
            )
        )

        # Call the original handler
        await self.app(scope, receive, send)
```

- Wraps the SSE transport's message handling with additional logging
- Follows the ASGI application interface pattern (scope, receive, send)
- Logs details about messages being processed by the server
- Delegates to the original message handling implementation from the SDK

## Health Check Endpoint

```python
async def health_check(request):
    """Health check endpoint."""
    request_id = str(uuid.uuid4())
    logger.debug(
        json.dumps(
            {
                "request_id": request_id,
                "message": "Health check called",
            }
        )
    )
    return JSONResponse({"status": "OK"})
```

- Simple health check endpoint that returns HTTP 200 and a JSON response
- Logs health check requests with a unique request ID
- Used for liveness and readiness probes in Kubernetes

## Starlette App Creation and Server Startup

```python
app = Starlette(
    routes=[
        Route("/", endpoint=health_check),
        Route("/health", endpoint=health_check),
        Route("/readiness", endpoint=health_check),
        Route("/liveness", endpoint=health_check),
        Route("/sse", endpoint=handle_sse),
        Mount("/messages", app=DebugMessageHandling(sse_transport.handle_post_message)),
    ]
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)

# Log information about configured routes
logger.info(f"Configured routes: {[route.path for route in app.routes]}")
logger.info("Server configured with SSE endpoint at: /sse")
logger.info("Message endpoint at: /messages/")
logger.info("Health check available at: /health")

# Run the server
port = int(os.environ.get("PORT", 8001))
logger.info({"request_id": str(uuid.uuid4()), "message": "MCP server starting up"})
uvicorn.run(app, host="0.0.0.0", port=port)
```

- Creates a Starlette application with routes for:
  - Health check endpoints (/, /health, /readiness, /liveness)
  - SSE connection endpoint (/sse)
  - Message posting endpoint (/messages)
- Adds the RequestLoggingMiddleware for request/response logging
- Logs information about the configured routes
- Starts the server using Uvicorn on the specified port (default: 8001)
- The order of routes is important for proper routing

## Entry Point

```python
if __name__ == "__main__":
    run_server()
```

- Standard Python idiom to run the server when the file is executed directly
- Calls the run_server function to start the MCP server
