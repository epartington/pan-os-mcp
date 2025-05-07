# Product Requirements Document (PRD): MCP Palo Alto Integration Server using Python MCP SDK

## 1. Overview

### 1.1 Purpose

This PRD outlines the requirements for an MCP (Model Context Protocol) server built using the **`modelcontextprotocol` Python SDK**. This server enables MCP clients (like Windsurf) to interface with Palo Alto Networks Next-Generation Firewall (NGFW) appliances and Panorama via their XML API. The application leverages the SDK's `FastMCP` abstraction to provide tool-calling capabilities for retrieving firewall configuration data.

### 1.2 Scope

The project includes:

- A Python-based MCP server built using the **`modelcontextprotocol` Python SDK**, primarily utilizing the `FastMCP` class and its decorators.
- A Python package for the Palo Alto MCP server following standard Python packaging practices (`pyproject.toml`) and installable via `pip` or `uv`.
- Integration with Palo Alto NGFW XML API for specific tool functions implemented as decorated Python functions.
- Support for both Palo Alto firewalls and Panorama with device group organization.
- Network transport using SSE (Server-Sent Events) for communicating with clients.
- Configuration primarily through environment variables (using `pydantic-settings`) and command-line arguments passed during server invocation.
- Seamless installation and development workflow using `uv` as recommended by the SDK.

**Out of Scope (for MVP):**

- Modifying firewall configurations (read-only tools initially).
- Advanced caching mechanisms for API responses.

### 1.3 Stakeholders

- **Product Owner**: [Your Name/Team]
- **Developers**: Backend team responsible for MCP server implementation using the Python SDK.
- **MCP Integration Team**: Team responsible for Python packaging and ensuring alignment with the Python MCP SDK ecosystem.
- **End Users**: Windsurf client team interfacing with Palo Alto NGFWs via MCP.

### 1.4 Timeline

- **Start Date**: April 10, 2025
- **MVP Release**: May 15, 2025 (Focus on core tools and SSE transport)
- **Full Release**: June 1, 2025

---

## 2. Goals and Objectives

### 2.1 Goals

- Enable MCP clients to query Palo Alto NGFW configurations through a standardized MCP interface.
- Provide a scalable, secure, and reliable MCP service built **using the `modelcontextprotocol` Python SDK**.
- Create a standard Python package easily installable via `pip`/`uv`.
- **Leverage the `FastMCP` abstraction** for rapid development and adherence to MCP patterns.
- Support both Palo Alto firewalls and Panorama management platform.
- Provide HTTP/SSE transport for seamless integration with modern MCP clients.

### 2.2 Objectives

- Implement four core tools using `@mcp.tool` decorator: `show_system_info`, `retrieve_address_objects`, `retrieve_security_zones`, `retrieve_security_policies`.
- Support Panorama device groups and shared objects for comprehensive address object management.
- Ensure compatibility with the MCP workflow for tool listing and calling as handled by `FastMCP`.
- Package the server as a standard Python module installable via `pip install .` or `uv pip install .`.
- Enable server configuration using environment variables with Pydantic Settings.
- Implement SSE transport support for modern client integration.
- Utilize the SDK's Pydantic integration for automatic request/response validation and strong typing.

---

## 3. Requirements

### 3.1 Functional Requirements

#### 3.1.1 MCP Server Functionality (using `FastMCP`)

- **FR1**: Implement a Python-based MCP server using the **`FastMCP` class** from the `modelcontextprotocol` SDK.
- **FR2**: Support the **SDK's HTTP/SSE transport** for network-based integration.
- **FR3**: Automatically expose available tools via the `FastMCP` handler for `list_tools` by using the `@mcp.tool` decorator.
- **FR4**: Automatically handle tool execution via the `FastMCP` handler for `call_tool` for functions decorated with `@mcp.tool`.
- **FR5**: Ensure tool results are automatically converted by `FastMCP` into the appropriate MCP format (e.g., `TextContent`).

#### 3.1.2 Palo Alto API Integration

- **FR6**: Connect to Palo Alto NGFW XML API using HTTPS (via `httpx`).
- **FR7**: Implement the `show_system_info` tool function.
- **FR8**: Implement the `retrieve_address_objects` tool function with support for both firewalls and Panorama device groups.
- **FR9**: Implement the `retrieve_security_zones` tool function.
- **FR10**: Implement the `retrieve_security_policies` tool function.

#### 3.1.3 Python Package Features

- **FR11**: Create a Python package defined using **`pyproject.toml`** and buildable with standard tools (`uv`, `build`).
- **FR12**: Provide a command-line entry point via `__main__.py` adhering to the SDK's structure.
- **FR13**: Include installation and usage documentation in `README.md`, referencing SDK installation methods.
- **FR14**: Accept configuration via **environment variables** managed using `pydantic-settings`.
- **FR15**: Follow the **project structure and patterns demonstrated in the `modelcontextprotocol` Python SDK examples**.

### 3.2 Non-Functional Requirements

#### 3.2.1 Performance

- **NFR1**: Process tool requests within 2 seconds (excluding Palo Alto API latency).
- **NFR2**: Leverage the SDK's underlying concurrency model (e.g., `anyio`) for handling requests.
- **NFR3**: Support SSE transport for efficient communication with clients.

#### 3.2.2 Security

- **NFR4**: Secure handling of API keys passed via environment variables. Do not hardcode credentials.
- **NFR5**: Leverage the **SDK's built-in Pydantic validation** for tool arguments via type hints.
- **NFR6**: Implement structured logging using standard Python logging.
- **NFR7**: Disable SSL verification only for development; recommend proper cert verification in production.

#### 3.2.3 Reliability

- **NFR8**: Implement proper error handling for Palo Alto API failures within tool functions, returning appropriate error messages via MCP.
- **NFR9**: Ensure graceful shutdown handled by the SDK's transport layer.
- **NFR10**: Provide clear error messages for both API and MCP interaction issues.

#### 3.2.4 Usability

- **NFR11**: Consistent installation process using `pip` or **`uv`**, aligning with other MCP Python packages.
- **NFR12**: Simple server configuration primarily via **environment variables with support for .env files**.
- **NFR13**: Easy-to-understand error messages for users/client developers.

---

## 4. Technical Specifications

### 4.1 Architecture

```
[Windsurf/MCP Client] --> [HTTP/SSE] --> [Python package: palo-alto-mcp (using FastMCP)] --> [Palo Alto NGFW/Panorama XML API]
```

### 4.2 Stack

- **Language**: Python (>=3.10, as per SDK)
- **MCP SDK**: **`modelcontextprotocol` Python SDK** (using `FastMCP`)
- **HTTP Client**: `httpx` for API requests
- **Schema Validation**: Pydantic (leveraged by `FastMCP`)
- **Configuration**: `pydantic-settings` for env var management
- **Packaging**: `pyproject.toml`, `hatchling`/`uv`
- **Development**: `uv`, `mypy`/`pyright`, `ruff` (as recommended by SDK)

### 4.3 Directory Structure

Following the `modelcontextprotocol` Python SDK example structure:

```
palo-alto-mcp/
├── src/
│   └── palo_alto_mcp/
│       ├── __init__.py           # Package initialization
│       ├── __main__.py           # Command-line entry point (runs server.main)
│       ├── config.py             # Configuration management with pydantic-settings
│       ├── server.py             # Main FastMCP server implementation, tool decorators
│       └── pan_os_api.py         # API client logic for Palo Alto NGFW XML API
├── tests/                    # Unit and integration tests
├── pyproject.toml            # Python package definition and build configuration
└── README.md                 # Documentation
```

### 4.4 MCP Implementation

- **Server:** Use `mcp.server.fastmcp.FastMCP`.
- **Tool Listing:** Automatic via `FastMCP` for `@mcp.tool` decorated functions.
- **Tool Execution:** Automatic via `FastMCP` for `@mcp.tool` decorated functions. Arguments validated by Pydantic.
- **Transport:** SDK's HTTP/SSE transport, accessible via `/sse` and `/messages/` endpoints.
- **Context:** Use the `mcp.server.fastmcp.Context` object within tools for logging.

### 4.5 Python Package Configuration

- **Package Name**: `palo-alto-mcp` (or similar, e.g., `palo_alto_mcp` for import)
- **Command**: Callable via `python -m palo_alto_mcp` which executes `server.main`. `server.main` calls `mcp.run(transport="sse")`.
- **Configuration**: Primarily via environment variables (e.g., `PANOS_HOSTNAME`, `PANOS_API_KEY`) loaded via `pydantic-settings`.
- **Version Management**: Managed in `pyproject.toml`.

---

## 5. User Stories

### 5.1 As a Windsurf Developer

- **US1**: I want the MCP server to automatically list its available Palo Alto tools so I can see what operations are possible.
- **US2**: I want to execute the `show_system_info` tool via MCP so I can get system information from the firewall.
- **US3**: I want to execute the `retrieve_address_objects` tool via MCP so I can get IP address object data from both firewalls and Panorama.
- **US4**: I want to execute the `retrieve_security_zones` tool via MCP so I can get network zone information.
- **US5**: I want to execute the `retrieve_security_policies` tool via MCP so I can access firewall rule configurations.
- **US6**: I want to install the MCP server easily using **`pip` or `uv`** so I don't need complex setup.
- **US7**: I want to configure the server using environment variables, consistent with SDK examples.
- **US8**: I want to connect to the server using HTTP/SSE transport to integrate with modern client workflows.

### 5.2 As an MCP Integration Engineer

- **US9**: I want to develop the server using the **`FastMCP` abstraction** provided by the Python SDK for simplicity and consistency.
- **US10**: I want to handle environment variables securely for API credentials, using `pydantic-settings`.
- **US11**: I want to provide clear `README.md` documentation for installation (`pip`/`uv`), configuration (env vars), and usage.
- **US12**: I want to use **Python type hints and the SDK's Pydantic integration** for strong typing of tool arguments and improved validation.
- **US13**: I want to support both Palo Alto firewalls and Panorama to provide comprehensive configuration access.

---

## 6. Acceptance Criteria

### 6.1 Tool Functionality

- Given valid Palo Alto API credentials (via env vars) and firewall hostname, when the `show_system_info` tool is called via MCP, then system information is returned as `TextContent`.
- Given valid Palo Alto API credentials, when the `retrieve_address_objects` tool is called via MCP, then a list of address objects is returned as `TextContent`, organized by location (shared, device group, or vsys).
- (Similar criteria for `retrieve_security_zones` and `retrieve_security_policies`).
- Given a running server, when a client calls the MCP `list_tools` method, then the definitions for all four Palo Alto tools (including names, descriptions, and Pydantic-generated argument schemas) are returned.

### 6.2 Python Package

- Given a Python environment with `uv` or `pip`, when I run `uv pip install .` or `pip install .` in the project root, then the package installs successfully.
- Given a client configuration pointing to the SSE endpoint (e.g., `http://localhost:8000/sse`), when the client launches, then it can successfully connect to the MCP server.
- Given environment variables set for `PANOS_HOSTNAME` and `PANOS_API_KEY`, when the server starts, then the tools can successfully authenticate and connect to the Palo Alto firewall API.

### 6.3 Integration

- Given a standard MCP client configured to connect to the SSE endpoint, then the client can successfully list and call the defined tools.
- Given a successful tool execution, when the Python tool function returns data, then `FastMCP` correctly converts it to `TextContent` and returns it to the client.
- Given a Panorama appliance as the target, when retrieving address objects, then objects are properly organized by device group and shared location.

### 6.4 Python Implementation (using SDK)

- The server implementation heavily utilizes the **`FastMCP` class**.
- Tool functions are defined using the **`@mcp.tool` decorator**.
- Tool arguments use **Python type hints** for validation via the SDK.
- The project structure matches the **SDK's example server structure**.
- The server uses the SSE transport via `mcp.run(transport="sse")`.

### 6.5 Security

- API credentials are only accepted via **environment variables** and are not hardcoded or logged.
- Invalid tool arguments provided by the client result in a validation error response generated by the **SDK's Pydantic integration**, rather than causing unexpected server behavior.

---

## 7. Risks and Mitigations

### 7.1 Risks

- **R1**: Palo Alto API rate limits could impact performance.
- **R2**: Complexity in parsing or handling the Palo Alto XML API responses reliably.
- **R3**: Different Palo Alto OS versions may have different XML structures.
- **R4**: SSL certificate validation may cause issues in development environments.

### 7.2 Mitigations

- **M1**: Implement basic retry logic in the API client (`pan_os_api.py`). Caching can be a future enhancement.
- **M2**: Use a robust XML parsing library (`xml.etree.ElementTree`) with comprehensive error handling.
- **M3**: Design the XML parsing to be flexible and handle different structures.
- **M4**: Allow SSL verification to be disabled for development but recommend proper cert verification in production.

---

## 8. Monitoring and Metrics

- **M1**: Configure structured logging using standard Python logging.
- **M2**: Include a debug mode (e.g., via env var) for verbose logging.
- **M3**: Log basic usage metrics like tool calls initiated and success/failure rates.

---

## 9. Implementation Plan

### 9.1 Phase 1: Project Setup and API Client (Completed)

- Set up Python project using **`uv` and `pyproject.toml`**, following the SDK's example structure.
- Create the basic `pan_os_api.py` client for connecting and authenticating to the Palo Alto XML API using `httpx`.
- Implement helper functions within `pan_os_api.py` to fetch and parse data for the required tools.
- Implement Panorama support with device group organization for address objects.

### 9.2 Phase 2: `FastMCP` Server Implementation (Completed)

- Implement the main `server.py` using **`FastMCP`**.
- Define the tool functions using the **`@mcp.tool` decorator**, calling the API client functions from Phase 1.
- Implement configuration loading from environment variables using `pydantic-settings`.
- Set up the `__main__.py` entry point to run the `FastMCP` server using SSE transport.

### 9.3 Phase 3: Testing and Documentation (In Progress)

- Write unit tests for the `pan_os_api.py` client.
- Write integration tests to verify tool listing and calling.
- Test manually with a client like Windsurf.
- Document installation (`uv`/`pip`), configuration (env vars), and usage in `README.md`.

### 9.4 Phase 4: Release (Pending)

- Build the package (`uv build`).
- Publish the package to a Python package registry (e.g., PyPI).
- Create release announcements.
- Gather feedback.

---

## 10. Success Metrics

- **S1**: Successfully installs via **`pip install` or `uv pip install`** in under 30 seconds.
- **S2**: Tool execution via MCP completes within 5 seconds (excluding API latency).
- **S3**: Zero compatibility issues reported when used with standard MCP clients connecting via SSE.
- **S4**: Positive feedback from client developers (e.g., Windsurf team) regarding ease of use and reliability.
- **S5**: Code maintainability confirmed by passing `ruff` and `pyright`/`mypy` checks as configured in `pyproject.toml`.

---

## 11. Future Enhancements

- **E1**: Support for additional Palo Alto API endpoints using `@mcp.tool`.
- **E2**: Implement caching for frequently requested API data within `pan_os_api.py`.
- **E3**: Add tools for modifying firewall configurations (requires careful design for safety and idempotency).
- **E4**: Enhanced error handling and reporting.
- **E5**: Support for authentication methods beyond API keys.