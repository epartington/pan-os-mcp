#!/usr/bin/env python
"""Debug test script for Palo Alto Networks MCP Server."""

import logging
import os
import sys

from palo_alto_mcp.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Test the configuration in debug mode."""
    # Set debug environment variable
    os.environ["PANOS_DEBUG"] = "true"

    # Test values for local debugging
    if "PANOS_HOSTNAME" not in os.environ:
        print("Setting test PANOS_HOSTNAME for debugging")
        os.environ["PANOS_HOSTNAME"] = "test-firewall.example.com"

    if "PANOS_API_KEY" not in os.environ:
        print("Setting test PANOS_API_KEY for debugging")
        os.environ["PANOS_API_KEY"] = "TEST_API_KEY_FOR_DEBUGGING"

    try:
        # Get settings and print them
        settings = get_settings()
        print("\n=== Configuration Settings ===")
        print(f"PANOS_HOSTNAME: {settings.panos_hostname}")
        print(f"PANOS_API_KEY: {'*' * 10} (masked for security)")
        print(f"DEBUG: {settings.debug}")
        print("============================\n")

        # You can import and run the server here if needed
        # from palo_alto_mcp.server import main as server_main
        # server_main()

        return 0
    except Exception as e:
        logger.error(f"Error in debug test: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
