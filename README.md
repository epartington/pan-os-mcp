# Palo Alto Networks MCP Server

A Model Context Protocol (MCP) server for interfacing with Palo Alto Networks Next-Generation Firewalls (NGFW) using the `modelcontextprotocol` Python SDK.

## Overview

This package provides an MCP server that enables MCP clients (like Windsurf) to interact with Palo Alto Networks NGFW appliances via their XML API. The server is built using the `FastMCP` abstraction from the `modelcontextprotocol` Python SDK and provides tool-calling capabilities for retrieving firewall configuration data.

## Features

- Retrieve address objects from Palo Alto Networks firewalls and Panorama
- Retrieve security zones from Palo Alto Networks firewalls
- Retrieve security policies from Palo Alto Networks firewalls
- Get system information from Palo Alto Networks firewalls
- Support for Panorama device groups and shared address objects
- Built using the `FastMCP` class from the `modelcontextprotocol` Python SDK
- Exposes network (HTTP/SSE) endpoints for integration with Windsurf and MCP clients

## Installation

### Prerequisites

- Python 3.10 or higher
- `uv` (recommended) or `pip`

### Install from Source

```bash
# Using uv (recommended)
uv pip install .

# Using pip
pip install .
```

## Configuration

The server requires the following environment variables to be set (can be provided via a `.env` file in the project root):

- `PANOS_HOSTNAME`: Hostname or IP address of the Palo Alto Networks NGFW
- `PANOS_API_KEY`: API key for authenticating with the Palo Alto Networks NGFW

Optional environment variables:

- `PANOS_DEBUG`: Set to `true` to enable debug logging (default: `false`)

Example `.env` file:

```
PANOS_HOSTNAME=192.168.1.1
PANOS_API_KEY=your-api-key-here
PANOS_DEBUG=true
```

## Usage

### Running the Server (Network/SSE mode)

```bash
python -m palo_alto_mcp
```

This will launch the MCP server as a network server, exposing HTTP/SSE endpoints for integration with Windsurf and other MCP clients.

### SSE Endpoints

- `/sse` — Main Server-Sent Events (SSE) endpoint for client-server communication
- `/messages/` — Message endpoint for SSE transport (required for Windsurf/MCP clients)

Ensure your client configuration points to these endpoints for correct operation.

### Integration with MCP Clients

The server is designed to be used with MCP clients like Windsurf. It follows the command-based integration pattern using the standard I/O transport provided by the SDK.

Example client configuration in `mcp_config.json`:

```json
{
  "tools": [
    {
      "name": "panos",
      "command": "palo-alto-mcp",
      "args": [],
      "env": {
        "PANOS_HOSTNAME": "192.168.1.1",
        "PANOS_API_KEY": "your-api-key-here"
      }
    }
  ]
}
```

## Available Tools

### `show_system_info`

Get system information from the Palo Alto Networks firewall.

**Example Response:**

```
# Palo Alto Networks Firewall System Information

**hostname**: fw01.example.com
**model**: PA-VM
**serial**: 0123456789
**sw-version**: 10.2.3
...
```

### `retrieve_address_objects`

Get address objects configured on the Palo Alto Networks firewall or Panorama. Address objects are grouped by location (shared, device group, or vsys).

**Example Response:**

```
# Palo Alto Networks Firewall Address Objects

## Shared Address Objects

### web-server
- **Type**: ip-netmask
- **Value**: 10.1.1.100/32
- **Description**: Web Server

## Device-group:Production Address Objects

### internal-network
- **Type**: ip-netmask
- **Value**: 10.1.0.0/16
- **Description**: Internal Network
- **Tags**: internal, production
```

### `retrieve_security_zones`

Get security zones configured on the Palo Alto Networks firewall.

**Example Response:**

```
# Palo Alto Networks Firewall Security Zones

## trust
- **Type**: layer3
- **Interfaces**:
  - ethernet1/1
  - ethernet1/2

## untrust
- **Type**: layer3
- **Interfaces**:
  - ethernet1/3
```

### `retrieve_security_policies`

Get security policies configured on the Palo Alto Networks firewall.

**Example Response:**

```
# Palo Alto Networks Firewall Security Policies

## allow-outbound
- **Description**: Allow outbound traffic
- **Action**: allow
- **Source Zones**:
  - trust
- **Source Addresses**:
  - any
- **Destination Zones**:
  - untrust
- **Destination Addresses**:
  - any
- **Applications**:
  - web-browsing
  - ssl
- **Services**:
  - application-default
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/cdot65/pan-os-mcp.git
cd pan-os-mcp

# Install development dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Run linting
ruff check .

# Run type checking
pyright
```

## Project Structure

```
palo-alto-mcp/
├── src/
│   └── palo_alto_mcp/
│       ├── __init__.py           # Package initialization
│       ├── __main__.py           # Command-line entry point
│       ├── config.py             # Configuration management
│       ├── server.py             # Main FastMCP server implementation
│       └── pan_os_api.py         # API client for Palo Alto NGFW XML API
├── tests/                        # Unit and integration tests
├── pyproject.toml                # Python package definition
└── README.md                     # Documentation
```

## License

MIT

## Patterns and Technologies Used

- **FastMCP**: Using the `FastMCP` class from the `modelcontextprotocol` Python SDK for MCP server implementation
- **Async/Await**: Using Python's async/await pattern for non-blocking I/O operations
- **Environment Variables**: Configuration via environment variables
- **Pydantic Settings**: Using `pydantic-settings` for configuration management
- **Type Hints**: Strong typing with Python type hints
- **Context Managers**: Using async context managers for resource management
- **XML Parsing**: Using the built-in `xml.etree.ElementTree` for parsing XML responses
- **Panorama Support**: Handling Panorama device groups and shared objects