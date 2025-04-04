# MCP Server Architecture

This document provides a comprehensive overview of the PAN-OS MCP server architecture, explaining how each component works together to create a functioning MCP server.

## Overall Architecture

The PAN-OS MCP server follows a modular architecture consisting of three key components:

1. **Main Server Module (`main.py`)**: The entry point that initializes and runs the MCP server with SSE transport
2. **Palo Alto API Module (`palo_alto_api.py`)**: Handles communication with the Palo Alto Networks firewall API
3. **Tools Module (`tools.py`)**: Defines and implements the MCP tools that clients can call

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│     main.py     │─────▶│    tools.py     │─────▶│palo_alto_api.py │
│  (Server Core)  │      │  (Tool Defs)    │      │  (API Client)   │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                                                  │
        │                                                  │
        ▼                                                  ▼
┌─────────────────┐                              ┌─────────────────┐
│   MCP Client    │                              │   Palo Alto     │
│   (Windsurf)    │◀─────────────────────────────│   Firewall      │
└─────────────────┘                              └─────────────────┘
```

## Communication Flow

1. The Windsurf MCP client connects to the server via the SSE endpoint (`/sse`)
2. The client sends tool requests to the message endpoint (`/messages/`)
3. The server processes the request through its tools module
4. If needed, the tools module calls the Palo Alto API module
5. The API module retrieves data from the firewall via HTTPS requests
6. Data flows back through the chain to the client as a response

## Server-Sent Events (SSE) Transport

The server uses SSE transport for communication with clients, which is a standard part of the MCP protocol:

- **SSE Connection**: Clients establish a persistent HTTP connection to `/sse`
- **Message Endpoint**: Clients send requests and receive responses via `/messages/`
- **Session Management**: Each connection is assigned a unique session ID for tracking

## Runtime Environment

The server operates in an async environment using:

- **Starlette/Uvicorn**: For the HTTP server and routing
- **anyio**: For asynchronous I/O operations
- **asyncio**: For the underlying async event loop
