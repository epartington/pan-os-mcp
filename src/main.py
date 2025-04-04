#!/usr/bin/env python
"""
MCP Palo Alto Integration Server Main Module

This module serves as the entry point for the MCP server that integrates
with Palo Alto Networks Next-Generation Firewall (NGFW) appliances.
"""

import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import List

import anyio
import mcp.types
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
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("asyncio").setLevel(logging.INFO)

logger = logging.getLogger("mcp-paloalto")


@asynccontextmanager
async def lifespan(app):
    """Server lifespan context manager for startup/shutdown operations."""
    # Startup: Log server start
    logger.info(json.dumps({"request_id": str(uuid.uuid4()), "message": "MCP server starting up"}))
    yield
    # Shutdown: Log server shutdown
    logger.info(json.dumps({"request_id": str(uuid.uuid4()), "message": "MCP server shutting down"}))


def create_mcp_server():
    """Create and configure the MCP server instance."""
    # Create MCP server instance
    server = Server(name="panos-mcp", version="1.0.0")

    # Register the list_tools handler using the decorator pattern
    @server.list_tools()
    async def handle_list_tools() -> List[mcp.types.Tool]:
        """List all available tools for the MCP server."""
        logger.info(json.dumps({"request_id": str(uuid.uuid4()), "message": "Listing available tools"}))
        return await list_tools()

    # Register tools with the server
    register_tools(server)

    return server


async def health_check(request):
    """Health check endpoint for the server.
    Returns a 200 OK response when the server is healthy.
    This endpoint can be used for Kubernetes liveness and readiness probes."""
    request_id = str(uuid.uuid4())
    logger.info(json.dumps({"request_id": request_id, "message": "Health check request received"}))
    return JSONResponse(
        {"status": "ok", "service": "mcp-paloalto", "request_id": request_id, "timestamp": anyio.current_time()}
    )


async def root_handler(request):
    """Root handler to provide basic info about the server."""
    return PlainTextResponse("PAN-OS MCP Server - Health check endpoint available at /health")


# Global MCP server instance
mcp_server = create_mcp_server()


async def run_server():
    """Run the MCP server with SSE transport and custom handlers."""
    port = int(os.environ.get("PORT", 8001))

    # Create the SSE transport with a specific endpoint for POST messages
    # This must be different from the GET endpoint for SSE connections
    sse_transport = SseServerTransport("/sse-messages/")
    logger.debug("Created SSE transport")

    # Create SSE handler that connects the transport to our MCP server
    async def handle_sse(request):
        """Handle SSE connections by connecting to the transport."""
        client = request.scope.get("client", ("unknown", 0))
        logger.info(f"New MCP SSE connection from {client[0]}:{client[1]}")

        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())

    # Define all routes
    routes = [
        Route("/", endpoint=root_handler),
        Route("/health", endpoint=health_check, methods=["GET"]),
        Route("/readiness", endpoint=health_check, methods=["GET"]),
        Route("/liveness", endpoint=health_check, methods=["GET"]),
        # The /sse endpoint handles GET requests for SSE connections
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        # The /sse-messages/ endpoint handles POST requests for sending messages
        Mount("/sse-messages/", app=sse_transport.handle_post_message),
    ]

    logger.info(f"Configured routes: {[r.path for r in routes if hasattr(r, 'path')]}")

    # Create and run Starlette app
    app = Starlette(routes=routes, lifespan=lifespan)

    # Log final setup information
    logger.info("Server configured with SSE endpoint at: /sse")
    logger.info("Health check available at: /health")

    # Start the server
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


def main():
    """Main entry point for the application."""
    try:
        anyio.run(run_server)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
