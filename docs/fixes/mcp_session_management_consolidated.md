# MCP Session Management - Consolidated Fix

## Issue Description

When working with the MCP server, we encountered a critical issue where clients received "Could not find session" errors despite having valid credentials. This document consolidates our analysis, findings, and the final solution to this session management problem.

## Root Cause Analysis

Our investigation revealed that the issue wasn't related to the Palo Alto API credentials, but rather stemmed from a fundamental misunderstanding of how session management works in the MCP SDK:

1. **Incorrect Session Management Approach**: We attempted to manually manage session IDs and track them in a custom dictionary (`active_sessions`), which conflicted with the SDK's built-in session management.

2. **Improper SSE Handler Implementation**: Our SSE connection handler didn't follow the pattern prescribed by the MCP SDK, causing disconnects between client sessions and server handling.

3. **Mismatched Asynchronous Context Management**: The connection streams weren't being properly maintained through the lifecycle of the SSE connection.

## MCP SDK Session Flow (Correct Model)

The MCP SDK uses the following flow for session management:

1. **Session Establishment**:
   - Client connects to the `/sse` endpoint
   - SDK generates a unique session ID (UUID)
   - SDK sends this ID to the client in the first SSE event
   - SDK maintains internal mapping of session IDs to stream writers

2. **Message Exchange**:
   - Client uses this session ID in subsequent requests to `/messages/`
   - SDK uses this ID to route messages to the correct session's streams
   - If a session ID is invalid or expired, the request is rejected

3. **Session Termination**:
   - When the SSE connection closes, the SDK cleans up the session automatically
   - Any subsequent requests using that session ID are rejected

## Solution Implementation

The solution was to follow the MCP SDK's prescribed pattern exactly, with additional error handling to gracefully manage client disconnections:

```python
async def handle_sse(request):
    """Handle SSE connection from client."""
    client = f"{request.client[0]}:{request.client[1]}" if request.client else "unknown"
    logger.info(f"New MCP SSE connection from {client}")

    # Set up initial response headers for SSE
    response = StreamingResponse(
        content=sse_stream_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
    return response

async def sse_stream_generator(request):
    """Generate the SSE stream for the client."""
    client = f"{request.client[0]}:{request.client[1]}" if request.client else "unknown"

    # Generate a unique ID for this connection for tracking
    connection_id = str(uuid.uuid4())
    logger.info(f"Starting SSE stream for {client} (id: {connection_id})")

    try:
        # First yield a comment to establish the connection
        yield b": connected\n\n"

        # Follow the exact pattern from the MCP SDK example
        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
            logger.info(f"SSE session established for {client} (id: {connection_id})")

            # Create initialization options
            init_options = mcp_server.create_initialization_options()

            # Run the MCP server with the streams
            try:
                await mcp_server.run(streams[0], streams[1], init_options)
            except anyio.BrokenResourceError as e:
                # This is expected when client disconnects
                logger.info(f"Client {client} (id: {connection_id}) disconnected: {str(e)}")
            except Exception as e:
                logger.error(f"Error during MCP server run for {client} (id: {connection_id}): {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Error in SSE stream for {client} (id: {connection_id}): {str(e)}", exc_info=True)
    finally:
        logger.info(f"SSE stream ended for {client} (id: {connection_id})")
```

Key changes included:

1. **Using a Proper Streaming Response Pattern**:
   - Implemented a dedicated `sse_stream_generator` coroutine
   - Returned a properly configured `StreamingResponse` object with appropriate headers
   - Added an initial connection message (`: connected`) to establish the connection

2. **Improved Exception Handling**:
   - Added explicit handling for `BrokenResourceError` which occurs when clients disconnect
   - Differentiated between connection issues and server runtime issues
   - Added comprehensive logging with connection IDs for better traceability

3. **Connection Lifecycle Management**:
   - Added unique tracking IDs for each connection
   - Implemented proper `finally` blocks to ensure cleanup regardless of how connections end
   - Added more detailed logging throughout the connection lifecycle

## Learnings

1. **Follow SDK Patterns**: The MCP SDK has a specific designed pattern for session management that should be followed exactly.

2. **Delegate to the SDK**: Instead of implementing custom session tracking, delegate this to the SDK's built-in mechanisms.

3. **Use Proper Async Patterns**: Use `async with` context managers for stream lifecycle management.

4. **Add Sufficient Logging**: Implement session lifecycle hooks to track session creation and termination.

5. **Keep Implementation Simple**: Avoid adding complexity that isn't required by the SDK design.

## Prevention

To avoid similar issues in the future:

1. **Study SDK Examples**: Always refer to SDK examples for the correct implementation patterns.

2. **Add Debugging Hooks**: Implement session lifecycle hooks for better visibility.

3. **Test Session Management**: Verify session establishment before making tool calls.

4. **Maintain Consistent Endpoint Configurations**: Ensure client and server use consistent paths (especially trailing slashes).

5. **Document Session Flow**: Maintain clear documentation of the session establishment and message exchange flow.

## References

- MCP SDK Example: `tmp/python-sdk/examples/servers/simple-tool/mcp_simple_tool/server.py`
- MCP Session Management Source: `tmp/python-sdk/src/mcp/server/sse.py`
