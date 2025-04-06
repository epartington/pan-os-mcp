"""Entry point for the Palo Alto Networks MCP Server."""

import sys

from palo_alto_mcp.server import main

if __name__ == "__main__":
    sys.exit(main())
