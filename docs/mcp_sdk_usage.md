# MCP Python SDK Usage Guide

This document explains how to use the MCP Python SDK to build custom MCP servers like the PAN-OS MCP server in this repository.

## SDK Overview

The MCP (Model Context Protocol) Python SDK provides a framework for building servers that can expose capabilities to MCP clients like Windsurf. The SDK follows a specific design pattern that makes it easy to:

1. Define and register tools
2. Handle client requests
3. Return structured responses
4. Support different transport mechanisms (SSE, stdio)

## Core SDK Components

The SDK is organized into several key components:

### 1. Server Class

The `Server` class from `mcp.server` is the central component that:

- Acts as a registry for tools
- Handles client connections
- Manages request/response flow
- Provides decorators for tool registration

```python
from mcp.server import Server

# Create a server instance with a unique name
mcp_server = Server("my-mcp-server")
```

### 2. Decorators for Tool Registration

The SDK uses decorators to register tools:

```python
# Register a function that lists available tools
@mcp_server.list_tools()
async def handle_list_tools():
    return [
        mcp.types.Tool(
            name="my_tool",
            description="Description of my tool",
            inputSchema={},
            run_in_new_process=False,
            is_user_tool=True,
        )
    ]

# Register a function that handles tool calls
@mcp_server.call_tool()
async def handle_tool_calls(name: str, params: dict):
    if name == "my_tool":
        # Tool implementation
        return [mcp.types.TextContent("Result")]
    else:
        raise ValueError(f"Unknown tool: {name}")
```

### 3. Response Types

The SDK provides different response types in `mcp.types`:

- `TextContent`: For returning text-based results
- `ImageContent`: For returning images
- `EmbeddedResource`: For returning complex embedded resources

```python
from mcp.types import TextContent

# Return text content
response = TextContent(json.dumps(result, indent=2))
```

### 4. Server Transport

The SDK supports different transport mechanisms:

#### SSE (Server-Sent Events)

For web-based clients:

```python
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route

# Create SSE transport
sse_transport = SseServerTransport("/messages/")

# Create SSE handler
async def handle_sse(request):
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )

# Create Starlette app with routes
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ],
)

# Run with Uvicorn
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8001)
```

#### STDIO

For command-line clients:

```python
from mcp.server.stdio import stdio_server
import anyio

async def run_server():
    async with stdio_server() as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )

anyio.run(run_server)
```

## Building an MCP Server: Step by Step

1. **Create a Server Instance**:

   ```python
   from mcp.server import Server
   mcp_server = Server("my-server-name")
   ```

2. **Define Tool Schemas**:

   ```python
   MY_TOOL_SCHEMA = {
       "type": "object",
       "properties": {
           "param1": {"type": "string", "description": "Description"},
           "param2": {"type": "number", "description": "Description"},
       },
       "required": ["param1"],
   }
   ```

3. **Register Tool Listing Function**:

   ```python
   @mcp_server.list_tools()
   async def handle_list_tools():
       return [
           mcp.types.Tool(
               name="my_tool",
               description="My tool description",
               inputSchema=MY_TOOL_SCHEMA,
               run_in_new_process=False,
               is_user_tool=True,
           )
       ]
   ```

4. **Register Tool Call Handler**:

   ```python
   @mcp_server.call_tool()
   async def handle_tool_calls(name: str, params: dict):
       if name == "my_tool":
           # Implement tool functionality
           result = do_something(params.get("param1"), params.get("param2"))
           return [mcp.types.TextContent(json.dumps(result))]
       else:
           raise ValueError(f"Unknown tool: {name}")
   ```

5. **Set Up Transport and Run Server**:

   ```python
   # For SSE transport
   sse_transport = SseServerTransport("/messages/")

   async def handle_sse(request):
       async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
           await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())

   # Create Starlette app
   app = Starlette(
       routes=[
           Route("/sse", endpoint=handle_sse),
           Mount("/messages/", app=sse_transport.handle_post_message),
       ],
   )

   # Run with Uvicorn
   uvicorn.run(app, host="0.0.0.0", port=8001)
   ```

## Best Practices

1. **Error Handling**: Wrap tool implementations in try/except blocks to handle failures gracefully.

2. **Validation**: Always validate input parameters before using them.

3. **Structured Logging**: Use structured logging with request IDs for easier debugging.

4. **Transport Configuration**: Ensure client and server endpoint configurations match exactly.

5. **Connection Handling**: Handle connection failures and client disconnections gracefully.

## Common Issues and Solutions

1. **BrokenResourceError**: Occurs when trying to send data to a disconnected client. Add exception handling:

   ```python
   try:
       await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())
   except anyio.BrokenResourceError:
       logger.warning("Client disconnected")
   ```

2. **Path Mismatches**: Ensure client configuration matches server paths exactly:
   - Server: `SseServerTransport("/messages/")`
   - Client: `"messageEndpoint": "http://localhost:8001/messages/"`

3. **Response Size**: Large responses may require increasing buffer sizes or implementing streaming.

## SDK Examples

The SDK includes several example implementations:

1. **Simple Tool Server**: Basic implementation of a tool-based server
2. **Simple Prompt Server**: Implementation of a prompt-based server
3. **Simple Resource Server**: Implementation of a resource-based server

These examples demonstrate different approaches to using the SDK and can be used as starting points for custom implementations.
