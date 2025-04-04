#!/usr/bin/env python
"""
MCP Palo Alto Integration Server Main Module

This module serves as the entry point for the MCP server that integrates
with Palo Alto Networks Next-Generation Firewall (NGFW) appliances.
"""

import json
import logging
import uuid
from contextlib import asynccontextmanager

import anyio
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route

from tools import list_tools, register_tools

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mcp-paloalto")


@asynccontextmanager
async def lifespan():
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
    # Register tools with the server
    register_tools(server)
    # Configure the server with list_tools handler
    server.list_tools_handler = list_tools
    return server


async def run_sse_server():
    """Run the MCP server with SSE transport."""
    server = create_mcp_server()
    # Create the SSE transport
    sse_transport = SseServerTransport("/messages/")

    # Define the SSE handler
    async def handle_sse(request):
        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(
                streams[0],
                streams[1],
                server.create_initialization_options(),
            )

    # Create Starlette routes
    routes = [
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]
    # Create and run Starlette app
    app = Starlette(routes=routes)
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


def main():
    """Main entry point for the application."""
    try:
        anyio.run(run_sse_server)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
