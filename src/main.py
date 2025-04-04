"""
MCP Server for Palo Alto Networks Firewall API

This server provides an MCP interface to interact with Palo Alto Networks firewalls,
allowing clients to retrieve address objects, security zones, and security policies.
"""

import json
import logging
import os
import traceback
import uuid
from typing import AsyncGenerator

import uvicorn
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Mount, Route

from tools import register_tools

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mcp-paloalto")
logger.setLevel(logging.DEBUG)


# Debug middleware to log all requests
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

    # Define an empty generator for streaming response
    async def empty_generator() -> AsyncGenerator[bytes, None]:
        """Generate an empty byte sequence for SSE response."""
        # This just yields once and then stops
        yield b""
        return

    # Handle SSE connection - follow the exact SDK example pattern
    async def handle_sse(request):
        """Handle SSE connection from client."""
        client = f"{request.client[0]}:{request.client[1]}" if request.client else "unknown"
        logger.info(f"New MCP SSE connection from {client}")

        try:
            # Follow the exact pattern from the MCP SDK example
            async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
                logger.info("SSE session established")
                # Create initialization options
                init_options = mcp_server.create_initialization_options()

                # Run the MCP server with the streams
                try:
                    await mcp_server.run(streams[0], streams[1], init_options)
                except Exception as e:
                    logger.error(f"Error during MCP server run: {str(e)}", exc_info=True)

        except Exception as e:
            logger.error(f"Error establishing SSE connection: {str(e)}", exc_info=True)
        finally:
            logger.info(f"SSE connection closed for client {client}")

        return StreamingResponse(
            content=empty_generator(),
            media_type="text/event-stream",
        )

    # Wrap the message handling with additional logging
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

    # Define health check endpoint
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

    # Create Starlette application with routes
    app = Starlette(
        routes=[
            Route("/", endpoint=health_check),
            Route("/health", endpoint=health_check),
            Route("/readiness", endpoint=health_check),
            Route("/liveness", endpoint=health_check),
            # Use standard Starlette request handler that delegates to ASGI
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


if __name__ == "__main__":
    run_server()
