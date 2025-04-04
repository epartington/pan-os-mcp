# MCP Connection Handling

This document explains in detail how the MCP connection works between the client and server, including common issues and their root causes.

## Connection Flow Overview

```
┌───────────────┐                                 ┌───────────────┐
│               │                                 │               │
│  MCP Client   │                                 │  MCP Server   │
│  (Windsurf)   │                                 │               │
│               │                                 │               │
└───────┬───────┘                                 └───────┬───────┘
        │                                                 │
        │  1. Initial SSE Connection                      │
        │ ──────────────────────────────────────────────► │
        │                                                 │
        │  2. SSE Connection Established                  │
        │ ◄─────────────────────────────────────────────  │
        │                                                 │
        │  3. POST Messages (e.g., ListTools)             │
        │ ──────────────────────────────────────────────► │
        │                                                 │
        │  4. Response via SSE Stream                     │
        │ ◄─────────────────────────────────────────────  │
        │                                                 │
        │  5. Tool Call (e.g., retrieve_address_objects)  │
        │ ──────────────────────────────────────────────► │
        │                                                 │
        │  6. Response via SSE Stream                     │
        │ ◄─────────────────────────────────────────────  │
        ▼                                                 ▼
```

## Connection Components

### 1. SSE Endpoint (`/sse`)

- **Purpose**: Establishes the initial Server-Sent Events connection
- **Implementation**: `handle_sse()` function in `main.py`
- **Protocol**: Uses HTTP GET request with persistent connection
- **Response Format**: Event stream with `data:` prefixed messages

### 2. Messages Endpoint (`/messages/`)

- **Purpose**: Receives client requests (ListTools, CallTool)
- **Implementation**: `sse_transport.handle_post_message` in `main.py`
- **Protocol**: Uses HTTP POST requests with session ID parameter
- **URL Format**: `/messages/?session_id=<unique_id>`

### 3. Stream Communication

- **Direction**: Bidirectional using separate streams
- **Client to Server**: Messages sent via POST requests
- **Server to Client**: Responses sent via SSE events
- **Connection Duration**: Persistent until client disconnects or error occurs

## Common Connection Issues

### 1. BrokenResourceError

```
File "/anyio/streams/memory.py", line 213, in send_nowait
    raise BrokenResourceError
anyio.BrokenResourceError
```

This critical error occurs when:
- The server tries to send a response via the SSE stream, but the client is no longer connected
- The stream's write buffer has been closed or broken due to client disconnection
- The server cannot properly send the response back to the client

**Root causes**:
- Client timeout settings too short for longer operations
- Network interruptions during API calls
- Client closing connection prematurely
- Mismatch between client and server endpoint configurations

### 2. Endpoint Path Mismatches

When the client and server use slightly different paths:
- Client: `messageEndpoint: "http://localhost:8001/messages"` (no trailing slash)
- Server: `sse_transport = SseServerTransport("/messages/")` (with trailing slash)

This causes:
- `307 Temporary Redirect` responses
- Extra round trips that may timeout
- Potential connection instability

### 3. Session Handling Issues

The SSE connection relies on proper session tracking:
- Each client connection gets a unique session ID
- All requests must include this session ID
- If session IDs are mismatched or expired, connections fail

## Environment Setup Requirements

For proper MCP connection:

1. **Client Configuration** (in `~/.codeium/windsurf/mcp_config.json`):
```json
{
  "mcpServers": {
    "panos": {
      "serverUrl": "http://localhost:8001/sse",
      "messageEndpoint": "http://localhost:8001/messages/",
      "options": {
        "hostname": "dallas.cdot.io",
        "api_key": "your-api-key"
      }
    }
  }
}
```

2. **Server Environment Variables** (in `.env`):
```
PANOS_API_KEY=your-api-key-here
PANOS_HOSTNAME=your-firewall-hostname
```

3. **Server Configuration** (in `main.py`):
```python
sse_transport = SseServerTransport("/messages/")
```

## Debugging Connection Issues

To troubleshoot connection problems:

1. **Check for Path Consistency**:
   - Ensure client `messageEndpoint` matches server `SseServerTransport` path
   - Both should use the same trailing slash convention

2. **Monitor HTTP Requests**:
   - Look for 307 redirects which indicate path mismatches
   - Check that all messages include proper session IDs

3. **Check Connection Timing**:
   - Long-running API calls might exceed client timeouts
   - Ensure firewall API responses are reasonably fast

4. **Verify Environment Variables**:
   - API credentials must be properly set in environment
   - Dotenv loading must happen before credentials are accessed

5. **Examine Error Stack Traces**:
   - `BrokenResourceError` typically indicates client disconnect
   - Look at the full stack trace to see where the error occurs in the process flow
