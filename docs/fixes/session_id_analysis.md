# MCP Session ID Handling Analysis

## Overview

This document analyzes how session IDs are managed in the MCP Server-Sent Events (SSE) implementation and how mismatches in session handling might contribute to the `BrokenResourceError` we're experiencing.

## How Session Management Works in MCP SDK

The MCP Python SDK handles session management through a combination of:

1. **SSE Connection**: Established when a client connects to the `/sse` endpoint
2. **Message Exchange**: Occurs through the `/messages/` endpoint
3. **Session ID Correlation**: Used to associate messages with specific SSE connections

### Session Creation Process

Based on our analysis of the MCP Python SDK:

1. When a client connects to the `/sse` endpoint, the server:
   - Generates a unique session ID
   - Stores the connection streams associated with this session ID
   - Returns the session ID to the client via the SSE connection

2. For subsequent messages, the client:
   - Includes this session ID in requests to the `/messages/` endpoint
   - The server uses this ID to look up the correct stream to send responses back

## Potential Issues in Our Implementation

### 1. Session ID Management

In our `main.py`, the session management relies entirely on the SDK's implementation:

```python
async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
    logger.info("SSE session established")
    await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())
```

The MCP SDK handles the session ID creation, but we don't:
- Log the generated session ID
- Perform any validation on incoming session IDs
- Have insight into session storage or lifecycle

### 2. Request Context Tracking

Our code lacks request context tracking between SSE connections and message endpoint calls:

```python
# We have this for initial SSE connection
client = request.scope.get("client", ("unknown", 0))
logger.info(f"New MCP SSE connection from {client[0]}:{client[1]}")

# But nothing similar for the message endpoint handling
```

This makes it difficult to correlate SSE connections with subsequent message requests.

### 3. Session Lifecycle Management

We don't handle session timeouts or cleanup:

```python
# We catch exceptions in the SSE handler:
except Exception as e:
    logger.exception(f"Error in SSE handler: {str(e)}")
    return JSONResponse({"error": "Connection error"}, status_code=500)

# But there's no explicit session cleanup or timeout logic
```

## Investigation Steps

To properly diagnose session ID issues, we should:

1. **Add Detailed Logging**:
   ```python
   async def handle_sse(request):
       """Handle an SSE connection request."""
       client = request.scope.get("client", ("unknown", 0))
       logger.info(f"New MCP SSE connection from {client[0]}:{client[1]}")

       try:
           # Extract and log session ID if present in query params
           session_id = request.query_params.get("session_id", "new-session")
           logger.info(f"Session ID: {session_id}")

           # This follows exactly the SDK example pattern
           async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
               logger.info("SSE session established")
               await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())
       except Exception as e:
           logger.exception(f"Error in SSE handler: {str(e)}")
           return JSONResponse({"error": "Connection error"}, status_code=500)
   ```

2. **Modify the Message Endpoint Mount**:
   ```python
   # Use a custom function to wrap the message endpoint handler
   async def message_handler(request):
       session_id = request.query_params.get("session_id")
       logger.info(f"Message received for session: {session_id}")
       return await sse_transport.handle_post_message(request)

   # Register the route with the custom handler
   Mount("/messages/", app=message_handler)
   ```

3. **Test Session Tracking**:
   - Implement a debugging endpoint that shows active sessions
   - Monitor session creation and expiration
   - Verify session IDs are correctly passing between client and server

## Hypotheses on `BrokenResourceError` Causes

1. **Path Redirection Breaks Session Context**:
   - When the client sends to `/messages/` but server has `/messages`
   - Redirect might not preserve query parameters or headers with session information
   - After redirect, server cannot associate message with original session

2. **Session Timeouts**:
   - Default session timeout in SDK may be too short for our API calls
   - Firewall API calls take longer than session timeout
   - By the time response is ready, session has expired

3. **Race Conditions**:
   - Client might send multiple requests using same session
   - Session handling in SDK might not be thread-safe
   - Concurrent access to same session streams causes corruption

## Recommended Fixes

1. **Fix Path Inconsistency** (as detailed in the separate document):
   ```python
   # Make sure these match:
   sse_transport = SseServerTransport("/messages/")
   Mount("/messages/", app=sse_transport.handle_post_message)
   # Client: "messageEndpoint": "http://localhost:8001/messages/"
   ```

2. **Add Session Debugging**:
   ```python
   # Add a session debug endpoint
   async def debug_sessions(request):
       # This requires access to SSE transport's internal session store
       # May need to modify SDK or add session tracking in our code
       return JSONResponse({"active_sessions": ["session_info"]})

   routes.append(Route("/debug/sessions", endpoint=debug_sessions))
   ```

3. **Improve Error Handling**:
   ```python
   async def handle_tool_call(name, params):
       session_id = get_current_session_id()
       try:
           # Tool implementation
           return [result]
       except Exception as e:
           logger.error(f"Error in session {session_id}: {str(e)}")
           raise
   ```

By addressing these session handling concerns, particularly ensuring path consistency and proper session tracking, we should be able to resolve the `BrokenResourceError` and improve the stability of our MCP server implementation.
