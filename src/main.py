"""
MCP Server for Palo Alto Networks Firewall API

This server provides an MCP interface to interact with Palo Alto Networks firewalls,
allowing clients to retrieve address objects, security zones, and security policies.
"""

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

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mcp-paloalto")
logger.setLevel(logging.DEBUG)


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

    # Create SSE handler that connects the transport to our MCP server
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

    # Define health check endpoint
    async def health_check(request):
        """Health check endpoint."""
        return JSONResponse({"status": "OK"})

    # Routes for the starlette app - exact order and pattern from SDK example
    routes = [
        Route("/", endpoint=health_check),
        Route("/health", endpoint=health_check),
        Route("/readiness", endpoint=health_check),
        Route("/liveness", endpoint=health_check),
        Route("/sse", endpoint=handle_sse),
        Mount("/messages", app=sse_transport.handle_post_message),
    ]

    # Create the starlette app with our routes
    app = Starlette(debug=True, routes=routes)

    # Log information about configured routes
    logger.info(f"Configured routes: {[route.path for route in routes]}")
    logger.info("Server configured with SSE endpoint at: /sse")
    logger.info("Health check available at: /health")

    # Run the server
    port = int(os.environ.get("PORT", 8001))
    logger.info({"request_id": str(uuid.uuid4()), "message": "MCP server starting up"})
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run_server()
