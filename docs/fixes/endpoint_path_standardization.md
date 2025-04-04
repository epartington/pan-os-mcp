# Endpoint Path Standardization Fix

## Issue Description

The documentation and possibly configuration contained inconsistent endpoint paths for the MCP server's SSE transport. Specifically:

- The README.md incorrectly referenced `/sse-messages/` for the message endpoint
- The correct path, according to MCP protocol specifications, should be `/messages/`

## Root Cause

This inconsistency violates the required pattern for SSE endpoints to work correctly with the Windsurf client:

1. The main SSE connection endpoint should be at `/sse`
2. The message endpoint for SSE transport should be at `/messages/` (not `/sse-messages/`)

The incorrect paths in the documentation could lead to connection failures between MCP clients and our server.

## Solution

Updated all documentation to maintain consistent endpoint paths that follow the MCP protocol specification:

1. Changed client configuration example in README.md to use:
   ```json
   {
     "endpoint": "http://localhost:8001/sse",
     "messageEndpoint": "http://localhost:8001/messages/"
   }
   ```

2. Updated the API Endpoints listing in README.md to show:
   - `/sse` - SSE connection endpoint
   - `/messages/` - Message posting endpoint

## Prevention

To prevent similar issues in the future:
- Review all documentation against actual implementation code
- Follow the MCP SDK examples closely for endpoint configurations
- Remember that both server configuration and client config must align on these paths

## Related Components

- README.md
- src/main.py (SSE transport configuration)
- Any client configuration files (.json)
