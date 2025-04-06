# Product Requirements Document (PRD): MCP Palo Alto Integration Server using Python MCP SDK

## 1. Overview

### 1.1 Purpose

This PRD outlines the requirements for an MCP (Model Context Protocol) server built _exclusively_ using the **`modelcontextprotocol` Python SDK**. This server enables MCP clients (like Windsurf) to interface with Palo Alto Networks Next-Generation Firewall (NGFW) appliances via their XML API. The application will leverage the SDK's `FastMCP` abstraction to provide tool-calling capabilities for retrieving firewall configuration data.

### 1.2 Scope

The project includes:

- A Python-based MCP server built using the **`modelcontextprotocol` Python SDK**, primarily utilizing the `FastMCP` class and its decorators.
- A Python package for the Palo Alto MCP server following standard Python packaging practices (`pyproject.toml`) and installable via `pip` or `uv`.
- Integration with Palo Alto NGFW XML API for specific tool functions implemented as decorated Python functions.
- Support for the MCP command-based integration pattern used by clients like Windsurf, leveraging the SDK's built-in stdio transport.
- Configuration primarily through environment variables (potentially using `pydantic-settings`) and command-line arguments passed during server invocation.
- Seamless installation and development workflow using `uv` as recommended by the SDK.

**Out of Scope (for MVP):**

- SSE transport mechanism (focus on stdio for command-based execution).
- Modifying firewall configurations (read-only tools initially).
- Features not directly supported or simplified by the `FastMCP` abstraction (unless explicitly required and justified).

### 1.3 Stakeholders

- **Product Owner**: [Your Name/Team]
- **Developers**: Backend team responsible for MCP server implementation using the Python SDK.
- **MCP Integration Team**: Team responsible for Python packaging and ensuring alignment with the Python MCP SDK ecosystem.
- **End Users**: Windsurf client team interfacing with Palo Alto NGFWs via MCP.

### 1.4 Timeline

- **Start Date**: April 10, 2025
- **MVP Release**: May 15, 2025 (Focus on stdio transport and core tools)
- **Full Release**: June 1, 2025

---

## 2. Goals and Objectives

### 2.1 Goals

- Enable MCP clients to query Palo Alto NGFW configurations through a standardized MCP interface.
- Provide a scalable, secure, and reliable MCP service built **using the `modelcontextprotocol` Python SDK**.
- Create a standard Python package easily installable via `pip`/`uv`.
- **Leverage the `FastMCP` abstraction** for rapid development and adherence to MCP patterns.
- Ensure seamless client integration through the command-based execution model supported by the SDK.

### 2.2 Objectives

- Implement three core tools using `@mcp.tool` decorator: `retrieve_address_objects`, `retrieve_security_zones`, `retrieve_security_policies`.
- Ensure compatibility with the MCP workflow for tool listing and calling as handled by `FastMCP`.
- Package the server as a standard Python module installable via `pip install .` or `uv pip install .`.
- Enable client configuration (server invocation) using the standard `command`/`args` pattern, facilitated by SDK tools like `mcp install` or direct execution.
- Simplify deployment leveraging the SDK's built-in stdio transport and execution methods (`mcp run` or `python -m ...`).
- Utilize the SDK's Pydantic integration for automatic request/response validation and strong typing.

---

## 3. Requirements

### 3.1 Functional Requirements

#### 3.1.1 MCP Server Functionality (using `FastMCP`)

- **FR1**: Implement a Python-based MCP server using the **`FastMCP` class** from the `modelcontextprotocol` SDK.
- **FR2**: Support the **SDK's built-in standard I/O transport** for command-line integration (`mcp.run()` or direct execution).
- **FR3**: Automatically expose available tools via the `FastMCP` handler for `list_tools` by using the `@mcp.tool` decorator.
- **FR4**: Automatically handle tool execution via the `FastMCP` handler for `call_tool` for functions decorated with `@mcp.tool`.
- **FR5**: Ensure tool results are automatically converted by `FastMCP` into the appropriate MCP format (e.g., `TextContent`).

#### 3.1.2 Palo Alto API Integration

- **FR6**: Connect to Palo Alto NGFW XML API using HTTPS (e.g., via `httpx`).
- **FR7**: Implement the `retrieve_address_objects` tool function.
- **FR8**: Implement the `retrieve_security_zones` tool function.
- **FR9**: Implement the `retrieve_security_policies` tool function.

#### 3.1.3 Python Package Features

- **FR10**: Create a Python package defined using **`pyproject.toml`** and buildable with standard tools (`uv`, `build`).
- **FR11**: Provide a command-line entry point via `__main__.py` adhering to the SDK's example structure (e.g., `python -m palo_alto_mcp.server`).
- **FR12**: Include installation and usage documentation in `README.md`, referencing SDK installation methods (`mcp install`, `uv pip install`).
- **FR13**: Accept configuration (API host, credentials) via **environment variables**, potentially managed using `pydantic-settings` as shown in SDK examples.
- **FR14**: Follow the **project structure and patterns demonstrated in the `modelcontextprotocol` Python SDK examples** (e.g., `examples/servers/simple-tool`).

### 3.2 Non-Functional Requirements

#### 3.2.1 Performance

- **NFR1**: Process tool requests within 2 seconds (excluding Palo Alto API latency).
- **NFR2**: Leverage the SDK's underlying concurrency model (e.g., `anyio`) for handling requests.
- **NFR3**: Minimize startup time for command-based execution.

#### 3.2.2 Security

- **NFR4**: Secure handling of API keys passed via environment variables. Do not hardcode credentials.
- **NFR5**: Leverage the **SDK's built-in Pydantic validation** for tool arguments via type hints and `Field` annotations.
- **NFR6**: Implement structured logging using the **SDK's logging utilities** (`mcp.server.fastmcp.utilities.logging`) or standard Python logging.

#### 3.2.3 Reliability

- **NFR7**: Implement proper error handling for Palo Alto API failures within tool functions, returning appropriate error messages via MCP.
- **NFR8**: Ensure graceful shutdown handled by the SDK's transport layer.
- **NFR9**: Provide clear error messages for both API and MCP interaction issues.

#### 3.2.4 Usability

- **NFR10**: Consistent installation process using `pip` or **`uv`**, aligning with other MCP Python packages.
- **NFR11**: Simple server configuration primarily via **environment variables and standard command-line arguments** during invocation (e.g., as set up by `mcp install`).
- **NFR12**: Easy-to-understand error messages for users/client developers.

---

## 4. Technical Specifications

### 4.1 Architecture

```
[Windsurf/MCP Client] --> [Python package: palo-alto-mcp (using FastMCP)] --> [Palo Alto NGFW XML API]
                      |
                MCP command-based execution via SDK's stdio transport
                (Invoked via `command`/`args` pattern, e.g., `uv run mcp run ...` or `python -m ...`)
```

### 4.2 Stack

- **Language**: Python (>=3.10, as per SDK)
- **MCP SDK**: **`modelcontextprotocol` Python SDK** (using `FastMCP`)
- **HTTP Client**: `httpx` (recommended by SDK) for API requests
- **Schema Validation**: Pydantic (leveraged by `FastMCP`)
- **Configuration**: `pydantic-settings` (optional, for env var management)
- **Packaging**: `pyproject.toml`, `hatchling`/`uv`
- **Development**: `uv`, `mypy`/`pyright`, `ruff` (as recommended by SDK)

### 4.3 Directory Structure

Following the `modelcontextprotocol` Python SDK example structure (`examples/servers/simple-tool`):

```
palo-alto-mcp/
├── src/
│   └── palo_alto_mcp/
│       ├── __init__.py           # Package initialization
│       ├── __main__.py           # Command-line entry point (runs server.main)
│       ├── server.py             # Main FastMCP server implementation, tool decorators
│       └── pan_os_api.py         # API client logic for Palo Alto NGFW XML API
├── tests/                    # Unit and integration tests
├── pyproject.toml            # Python package definition and build configuration
└── README.md                 # Documentation
```

_(Note: Tool function definitions using `@mcp.tool` reside directly in `server.py`)_

### 4.4 MCP Implementation

- **Server:** Use `mcp.server.fastmcp.FastMCP`.
- **Tool Listing:** Automatic via `FastMCP` for `@mcp.tool` decorated functions.
- **Tool Execution:** Automatic via `FastMCP` for `@mcp.tool` decorated functions. Arguments validated by Pydantic.
- **Transport:** SDK's standard I/O transport, invoked via `mcp.run()`.
- **Context:** Use the `mcp.server.fastmcp.Context` object within tools for logging or progress reporting if needed.

### 4.5 Python Package Configuration

- **Package Name**: `palo-alto-mcp` (or similar, e.g., `palo_alto_mcp` for import)
- **Command**: Callable via `python -m palo_alto_mcp` (or `python -m palo_alto_mcp.server`) which executes `server.main`. `server.main` should call `mcp.run()`.
- **Configuration**: Primarily via environment variables (e.g., `PANOS_HOSTNAME`, `PANOS_API_KEY`) loaded possibly via `pydantic-settings`. Command-line args for the _invocation_ (like debug flags) can be handled if needed, but core config via env vars preferred.
- **Version Management**: Use `uv-dynamic-versioning` or similar, managed in `pyproject.toml`.

---

## 5. User Stories

### 5.1 As a Windsurf Developer

- **US1**: I want the MCP server to automatically list its available Palo Alto tools so I can see what operations are possible.
- **US2**: I want to execute the `retrieve_address_objects` tool via MCP so I can get IP address object data from the firewall.
- **US3**: I want to execute the `retrieve_security_zones` tool via MCP so I can get network zone information.
- **US4**: I want to execute the `retrieve_security_policies` tool via MCP so I can access firewall rule configurations.
- **US5**: I want to install the MCP server easily using **`pip` or `uv`** so I don't need complex setup.
- **US6**: I want to configure the server **invocation** in my client config using the standard command/args pattern, and configure the server's **behavior** (like API keys) using environment variables, consistent with SDK examples and tools like `mcp install`.

### 5.2 As an MCP Integration Engineer

- **US7**: I want to develop the server using the **`FastMCP` abstraction** provided by the Python SDK for simplicity and consistency.
- **US8**: I want to handle environment variables securely for API credentials, potentially using `pydantic-settings`.
- **US9**: I want to provide clear `README.md` documentation for installation (`pip`/`uv`), configuration (env vars), and usage.
- **US10**: I want to use **Python type hints and the SDK's Pydantic integration** for strong typing of tool arguments and improved validation.

---

## 6. Acceptance Criteria

### 6.1 Tool Functionality

- Given valid Palo Alto API credentials (via env vars) and firewall hostname, when the `retrieve_address_objects` tool is called via MCP, then a list of address objects is returned as `TextContent`.
- (Similar criteria for `retrieve_security_zones` and `retrieve_security_policies`).
- Given a running server, when a client calls the MCP `list_tools` method, then the definitions for the three Palo Alto tools (including names, descriptions, and Pydantic-generated argument schemas) are returned.

### 6.2 Python Package

- Given a Python environment with `uv` or `pip`, when I run `uv pip install .` or `pip install .` in the project root, then the package installs successfully.
- Given a client configuration using the command/args pattern pointing to the installed package's entry point (e.g., `python -m palo_alto_mcp`), when the client launches the server, then the `FastMCP` server starts correctly using stdio transport.
- Given environment variables set for `PANOS_HOSTNAME` and `PANOS_API_KEY`, when the server starts, then the tools can successfully authenticate and connect to the Palo Alto firewall API.

### 6.3 Integration

- Given a standard MCP client configured to invoke the server using the command/args pattern, then the client can successfully list and call the defined tools.
- Given a successful tool execution, when the Python tool function returns data, then `FastMCP` correctly converts it to `TextContent` and returns it to the client.

### 6.4 Python Implementation (using SDK)

- The server implementation heavily utilizes the **`FastMCP` class**.
- Tool functions are defined using the **`@mcp.tool` decorator**.
- Tool arguments use **Python type hints** (and optionally `pydantic.Field`) for validation via the SDK.
- The project structure matches the **SDK's example server structure**.

### 6.5 Security

- API credentials are only accepted via **environment variables** and are not hardcoded or logged.
- Invalid tool arguments provided by the client result in a validation error response generated by the **SDK's Pydantic integration**, rather than causing unexpected server behavior.

---

## 7. Risks and Mitigations

### 7.1 Risks

- **R1**: Palo Alto API rate limits could impact performance.
- **R2**: Complexity in parsing or handling the Palo Alto XML API responses reliably.
- **R3**: Ensuring compatibility with various Python environments and dependency conflicts (mitigated by `uv`).

### 7.2 Mitigations

- **M1**: Implement basic retry logic in the API client (`pan_os_api.py`). Caching can be a future enhancement.
- **M2**: Use a robust XML parsing library (e.g., `xml.etree.ElementTree`, `lxml`) and potentially Pydantic models for API response validation within `pan_os_api.py`.
- **M3**: Use `uv` for dependency management and clearly document Python version requirements (>=3.10). Perform testing in clean environments.

---

## 8. Monitoring and Metrics

- **M1**: Configure structured logging using the **SDK's utilities** or standard Python logging, including request/tool identifiers.
- **M2**: Include a debug mode (e.g., via env var or CLI flag handled by `FastMCP` or `server.py`) for verbose logging.
- **M3**: Log basic usage metrics like tool calls initiated and success/failure rates.

---

## 9. Implementation Plan

### 9.1 Phase 1: Project Setup and API Client (1 week)

- Set up Python project using **`uv` and `pyproject.toml`**, following the SDK's example structure.
- Create the basic `pan_os_api.py` client for connecting and authenticating to the Palo Alto XML API using `httpx`.
- Implement helper functions within `pan_os_api.py` to fetch and parse data for the three required tools (address objects, zones, policies).

### 9.2 Phase 2: `FastMCP` Server Implementation (2 weeks)

- Implement the main `server.py` using **`FastMCP`**.
- Define the three tool functions using the **`@mcp.tool` decorator**, calling the API client functions from Phase 1.
- Implement configuration loading from environment variables (e.g., using `pydantic-settings`).
- Set up the `__main__.py` entry point to run the `FastMCP` server using `mcp.run()`.

### 9.3 Phase 3: Testing and Documentation (1 week)

- Write unit tests for the `pan_os_api.py` client.
- Write integration tests using the **SDK's test utilities** (e.g., `create_connected_server_and_client_session`) to verify tool listing and calling.
- Test manually with a client like Windsurf or the MCP Inspector (`mcp dev`).
- Document installation (`uv`/`pip`), configuration (env vars), and usage in `README.md`.

### 9.4 Phase 4: Release (1 week)

- Build the package (`uv build`).
- Publish the package to a Python package registry (e.g., PyPI).
- Create release announcements.
- Gather feedback.

---

## 10. Success Metrics

- **S1**: Successfully installs via **`pip install` or `uv pip install`** in under 30 seconds.
- **S2**: Tool execution via MCP completes within 5 seconds (excluding API latency).
- **S3**: Zero compatibility issues reported when used with standard MCP clients invoking the server via command/args.
- **S4**: Positive feedback from client developers (e.g., Windsurf team) regarding ease of use and reliability.
- **S5**: Code maintainability confirmed by passing `ruff` and `pyright`/`mypy` checks as configured in `pyproject.toml`.

---

## 11. Future Enhancements

- **E1**: Support for additional Palo Alto API endpoints using `@mcp.tool`.
- **E2**: Implement caching for frequently requested API data within `pan_os_api.py`.
- **E3**: Add tools for modifying firewall configurations (requires careful design for safety and idempotency).
- **E4**: Support for SSE transport using the SDK if required by other clients.
- **E5**: More sophisticated error handling and reporting.
