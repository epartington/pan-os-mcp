#!/usr/bin/env python
"""
Test client for the PAN-OS MCP Server.

This script creates a simple MCP client that connects to your local MCP server
and tries to retrieve address objects. It follows the correct session initialization
pattern required by the MCP protocol.
"""

import asyncio
import json
import logging

from mcp import ClientSession
from mcp.client.sse import sse_client

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("test-client")


async def run_test_client():
    """Run a test MCP client that connects to the local server."""

    # Configure the endpoint for your server
    server_url = "http://localhost:8001"
    sse_endpoint = f"{server_url}/sse"

    logger.info(f"Connecting to MCP server at {sse_endpoint}")

    # Create the SSE client connection with the correct endpoint
    try:
        async with sse_client(sse_endpoint) as streams:
            # Create client session with the transport streams
            logger.info("Creating MCP client session")
            read_stream, write_stream = streams

            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the session - this is critical!
                logger.info("Initializing session")
                await session.initialize()

                logger.info("Session initialized, listing available tools")

                # List available tools
                tools = await session.list_tools()
                logger.info(f"Available tools: {[tool.name for tool in tools]}")

                # Call the retrieve_address_objects tool
                logger.info("Calling retrieve_address_objects tool")
                try:
                    results = await session.call_tool("retrieve_address_objects", {"location": "vsys", "vsys": "vsys1"})
                    # Print results
                    logger.info("Tool call successful")
                    for result in results:
                        if hasattr(result, "text"):
                            parsed = json.loads(result.text)
                            logger.info(f"Found {len(parsed)} address objects")
                            for obj in parsed:
                                logger.info(f"  - {obj['name']} ({obj['type']}): {obj['value']}")
                        else:
                            logger.info(f"Result: {result}")
                except Exception as e:
                    logger.error(f"Error calling tool: {str(e)}")
    except Exception as e:
        logger.error(f"Error connecting to MCP server: {str(e)}")


if __name__ == "__main__":
    asyncio.run(run_test_client())
