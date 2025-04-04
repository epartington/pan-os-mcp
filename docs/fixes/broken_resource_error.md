# BrokenResourceError Fix Document

## Problem Description

When using the PAN-OS MCP server, we consistently encountered a `BrokenResourceError` during tool calls, specifically when attempting to retrieve address objects from the firewall. The connection would break at the exact moment when the server tried to send the response back to the client.

```python
File "/anyio/streams/memory.py", line 213, in send_nowait
    raise BrokenResourceError
anyio.BrokenResourceError
```

This error would occur after:
1. Successfully connecting to the SSE endpoint
2. Successfully making tool calls
3. Successfully retrieving data from the Palo Alto firewall API
4. Attempting to send the response back to the client

## Root Cause Analysis

After careful analysis, we identified several potential causes:

1. **Endpoint Path Mismatch**: The client and server had inconsistent endpoint path configurations:
   - Server: `sse_transport = SseServerTransport("/messages/")`
   - Client: `"messageEndpoint": "http://localhost:8001/messages"`

2. **Connection Timing**: The firewall API calls would take longer than the client's connection timeout.

3. **Session Handling**: The session might be terminated prematurely by either the client or server.

4. **Response Size**: The response data may be too large for the default buffer size.

## Solution Approaches

We tried several approaches to fix this issue:

1. **Aligning Endpoint Paths**: Modified the client configuration to match the server's endpoint format exactly:
   ```json
   "messageEndpoint": "http://localhost:8001/messages/"
   ```

   This eliminated the 307 redirects but did not fix the BrokenResourceError.

2. **Server-Side Handling**: The fundamental issue is with the MCP SDK's handling of the connection closing:
   - The error occurs in the `anyio` library's memory stream implementation
   - When the client disconnects, the server tries to send data to a closed stream
   - This is a common issue in SSE implementations where the client may disconnect unexpectedly

## Successful Solution

The most effective solution involves implementing more robust error handling in the server:

1. **Add Exception Handling**: In the `handle_tool_call` function, wrap the response sending in additional try/except blocks:

```python
async def handle_tool_call(name: str, params: Dict) -> List[TextContent]:
    request_id = str(uuid.uuid4())
    logger.info(json.dumps({"request_id": request_id, "message": f"Tool call: {name}", "params": params}))

    try:
        if name == "retrieve_address_objects":
            return [await retrieve_address_objects(params, request_id)]
        elif name == "retrieve_security_zones":
            return [await retrieve_security_zones(params, request_id)]
        elif name == "retrieve_security_policies":
            return [await retrieve_security_policies(params, request_id)]
        else:
            raise ValueError(f"Unknown tool: {name}")
    except anyio.BrokenResourceError:
        # Connection was closed by client, log it but don't crash
        logger.warning(json.dumps({
            "request_id": request_id,
            "message": "Client disconnected before response could be sent"
        }))
        # Return empty list to satisfy the function signature
        return []
    except Exception as e:
        logger.error(json.dumps({
            "request_id": request_id,
            "message": f"Error in tool call: {str(e)}"
        }))
        # Still need to return something or the server will crash
        return [TextContent(json.dumps({"error": str(e)}))]
```

2. **Modify Main Server Loop**: Add exception handling in the main SSE connection handler:

```python
async def handle_sse(request):
    """Handle an SSE connection request."""
    logger.debug(f"SSE request details: {request.url.path}, {dict(request.query_params)}")
    client = request.scope.get("client", ("unknown", 0))
    logger.info(f"New MCP SSE connection from {client[0]}:{client[1]}")

    try:
        # This follows exactly the SDK example pattern
        async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
            logger.info("SSE session established")
            try:
                await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())
            except anyio.BrokenResourceError:
                logger.warning(f"Client {client[0]}:{client[1]} disconnected")
                # Just let the connection close gracefully
                return JSONResponse({"status": "disconnected"})
    except Exception as e:
        logger.exception(f"Error in SSE handler: {str(e)}")
        return JSONResponse({"error": "Connection error"}, status_code=500)
```

3. **Client-Side Improvements**: Ensure the client maintains connections for longer operations:
   - Increase connection timeout settings
   - Implement reconnection logic

## Lessons Learned

1. **SSE Connection Management**: Server-Sent Events connections require careful handling of client disconnections.

2. **Path Consistency**: Client and server endpoint paths must match exactly to avoid redirects.

3. **Robust Error Handling**: Any code that sends responses over network connections must handle connection losses gracefully.

4. **Request/Response Cycle**: The entire cycle from request to API call to response must be protected against premature disconnections.

This issue is common in SSE implementations and requires defensive programming techniques to handle gracefully.
