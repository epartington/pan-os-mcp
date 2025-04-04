#!/usr/bin/env python
"""
MCP Palo Alto Integration Server Main Module

This module serves as the entry point for the MCP server that integrates
with Palo Alto Networks Next-Generation Firewall (NGFW) appliances.
"""

import logging
import os
import uuid
from contextlib import asynccontextmanager

import anyio
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Mount, Route

from tools import list_tools, register_tools

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# Set specific loggers to lower levels for less noise
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)

# Create a custom logger for this application
logger = logging.getLogger("mcp-paloalto")
logger.setLevel(logging.DEBUG)

# Initialize the MCP server
mcp_server = Server("panos-mcp", "1.0.0")


@asynccontextmanager
async def lifespan(app):
    """Lifecycle manager for the Starlette app."""
    # Log server startup with a request ID for tracking
    request_id = str(uuid.uuid4())
    logger.info({"request_id": request_id, "message": "MCP server starting up"})
    yield
    # Log server shutdown
    shutdown_request_id = str(uuid.uuid4())
    logger.info({"request_id": shutdown_request_id, "message": "MCP server shutting down"})


async def health_check(request):
    """Health check endpoint that returns a 200 OK response."""
    return PlainTextResponse("OK")


async def root_handler(request):
    """Root endpoint that returns a simple JSON response."""
    return JSONResponse({"status": "ok", "message": "MCP server is running"})


async def run_server():
    """Run the MCP server with SSE transport and custom handlers."""
    port = int(os.environ.get("PORT", 8001))

    # Initialize the MCP server
    mcp_server = Server("panos-mcp", "1.0.0")

    # Register the list_tools handler
    @mcp_server.list_tools()
    async def handle_list_tools():
        """Return the list of available tools."""
        request_id = str(uuid.uuid4())
        logger.info({"request_id": request_id, "message": "Listing available tools"})
        return await list_tools()

    # Register the MCP tools for calling
    register_tools(mcp_server)

    # Create the SSE transport with a specific endpoint for POST messages
    sse_transport = SseServerTransport("/messages/")
    logger.debug("Created SSE transport")

    # Create SSE handler that connects the transport to our MCP server
    async def handle_sse(request):
        """Handle an SSE connection request."""
        logger.debug(f"SSE request details: {request.url.path}, {dict(request.query_params)}")
        client = request.scope.get("client", ("unknown", 0))
        logger.info(f"New MCP SSE connection from {client[0]}:{client[1]}")

        try:
            # Establish the SSE connection using the transport
            async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
                logger.info("SSE session established")
                # Run the MCP server with the SSE streams
                await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())
        except Exception as e:
            logger.exception(f"Error in SSE handler: {str(e)}")
            return JSONResponse({"error": "Connection error"}, status_code=500)

    # Define all routes
    routes = [
        Route("/", endpoint=root_handler),
        Route("/health", endpoint=health_check),
        Route("/readiness", endpoint=health_check),
        Route("/liveness", endpoint=health_check),
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]

    route_paths = [route.path for route in routes]
    logger.info(f"Configured routes: {route_paths}")
    logger.info("Server configured with SSE endpoint at: /sse")
    logger.info("Health check available at: /health")

    # Create and run the Starlette app
    app = Starlette(routes=routes, lifespan=lifespan)

    # Configure the server
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)

    # Start the server
    await server.serve()


if __name__ == "__main__":
    # Run the server
    anyio.run(run_server)
