"""
Entry point for the Palo Alto Networks MCP Server.

Launches the server as a network (SSE/HTTP) MCP server, exposing /sse and /messages/ endpoints.
"""

from palo_alto_mcp.server import main

if __name__ == "__main__":
    main()
