#!/usr/bin/env python
"""Run the Palo Alto Networks MCP Server in debug mode."""

import logging
import os
import sys

from palo_alto_mcp.server import main as server_main

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def setup_debug_environment() -> None:
    """Set up environment variables for debugging."""
    # Enable debug mode
    os.environ["PANOS_DEBUG"] = "true"

    # Set test values if not already set
    if "PANOS_HOSTNAME" not in os.environ:
        logger.info("Setting test PANOS_HOSTNAME for debugging")
        os.environ["PANOS_HOSTNAME"] = "test-firewall.example.com"

    if "PANOS_API_KEY" not in os.environ:
        logger.info("Setting test PANOS_API_KEY for debugging")
        os.environ["PANOS_API_KEY"] = "TEST_API_KEY_FOR_DEBUGGING"


def main() -> int:
    """Run the MCP server in debug mode."""
    try:
        # Set up debug environment
        setup_debug_environment()

        # Start the server
        logger.info("Starting Palo Alto Networks MCP Server in debug mode")
        server_main()

        return 0
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
