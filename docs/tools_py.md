# tools.py Documentation

This document provides a comprehensive explanation of the `tools.py` module, which defines and implements all the MCP tools available to clients.

## File Purpose

`tools.py` serves as the core tools implementation for the MCP server. It:
- Defines the schemas for each tool
- Implements the tool business logic
- Handles parameter validation
- Registers tools with the MCP server
- Formats responses as TextContent

## Import Statements

```python
import json
import logging
import uuid
from typing import Dict, List

import mcp
from mcp.server import Server
from mcp.types import TextContent

from palo_alto_api import PaloAltoApiError, get_address_objects, get_security_policies, get_security_zones
```

### Import Details

- **Standard Library Imports**:
  - `json`: For serializing/deserializing API responses
  - `logging`: For structured logging
  - `uuid`: To generate unique request identifiers
  - `typing`: For type hints (Dict, List)

- **MCP SDK Imports**:
  - `mcp`: The core MCP framework
  - `mcp.server.Server`: Server class for registering tools
  - `mcp.types.TextContent`: Response type for tool results

- **Local Imports**:
  - Functions from `palo_alto_api.py`: To interact with the firewall API
  - `PaloAltoApiError`: Custom exception from the API module

## Logging Configuration

```python
# Configure logging
logger = logging.getLogger("mcp-paloalto.tools")
```

- Creates a logger instance for the tools module with namespace "mcp-paloalto.tools"

## Tool Schema Definitions

```python
# Tool schemas
ADDRESS_OBJECTS_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "location": {"type": "string", "description": "Location type (e.g., vsys, shared)", "default": "vsys"},
        "vsys": {"type": "string", "description": "VSYS identifier", "default": "vsys1"},
    },
    "required": ["location", "vsys"],
}

SECURITY_ZONES_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "location": {"type": "string", "description": "Location type (e.g., vsys, shared)", "default": "vsys"},
        "vsys": {"type": "string", "description": "VSYS identifier", "default": "vsys1"},
    },
    "required": ["location", "vsys"],
}

SECURITY_POLICIES_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "location": {"type": "string", "description": "Location type (e.g., vsys, shared)", "default": "vsys"},
        "vsys": {"type": "string", "description": "VSYS identifier", "default": "vsys1"},
    },
    "required": ["location", "vsys"],
}
```

- Defines JSON Schema for each tool's parameters
- Each schema:
  - Has `type: "object"` for structured parameters
  - Defines properties with their types and descriptions
  - Provides default values for convenience
  - Specifies which parameters are required

## Tools Listing Function

```python
async def list_tools() -> List[mcp.types.Tool]:
    """List all available tools for the MCP server.

    Returns:
        List of tool definitions
    """
    logger.info(json.dumps({"request_id": str(uuid.uuid4()), "message": "Listing available tools"}))

    return [
        mcp.types.Tool(
            name="retrieve_address_objects",
            description="Retrieve address objects from a Palo Alto Networks firewall",
            inputSchema=ADDRESS_OBJECTS_TOOL_SCHEMA,
            run_in_new_process=False,
            is_user_tool=True,
        ),
        mcp.types.Tool(
            name="retrieve_security_zones",
            description="Retrieve security zones from a Palo Alto Networks firewall",
            inputSchema=SECURITY_ZONES_TOOL_SCHEMA,
            run_in_new_process=False,
            is_user_tool=True,
        ),
        mcp.types.Tool(
            name="retrieve_security_policies",
            description="Retrieve security policies from a Palo Alto Networks firewall",
            inputSchema=SECURITY_POLICIES_TOOL_SCHEMA,
            run_in_new_process=False,
            is_user_tool=True,
        ),
    ]
```

- Creates and returns list of all available tools
- Logs the tool listing action with a unique request ID
- Each tool is defined with:
  - `name`: Unique identifier for the tool
  - `description`: Human-readable description
  - `inputSchema`: JSON Schema for tool parameters
  - `run_in_new_process=False`: Tools run in the same process
  - `is_user_tool=True`: Tools are available to users

## Tool Registration Function

```python
def register_tools(server: Server) -> None:
    """Register all tools with the MCP server."""

    # Register list_tools handler
    @server.list_tools()
    async def handle_list_tools():
        """Return the list of available tools."""
        request_id = str(uuid.uuid4())
        logger.info(json.dumps({"request_id": request_id, "message": "Listing available tools"}))
        return await list_tools()
```

- Main function to register all tools with the MCP server
- Takes a Server instance as parameter
- Uses the `@server.list_tools()` decorator to register the tools listing handler
- The handler generates a unique request ID and returns the list of tools

## Tool Call Handler

```python
# Register a single call_tool handler that dispatches to different tools based on name
@server.call_tool()
async def handle_tool_call(name: str, params: Dict) -> List[TextContent]:
    """
    Handle all tool calls and dispatch to the appropriate function.

    Args:
        name: The name of the tool to call
        params: Tool parameters

    Returns:
        List of content objects with tool results
    """
    request_id = str(uuid.uuid4())
    logger.info(json.dumps({"request_id": request_id, "message": f"Tool call: {name}", "params": params}))

    if name == "retrieve_address_objects":
        return [await retrieve_address_objects(params, request_id)]
    elif name == "retrieve_security_zones":
        return [await retrieve_security_zones(params, request_id)]
    elif name == "retrieve_security_policies":
        return [await retrieve_security_policies(params, request_id)]
    else:
        raise ValueError(f"Unknown tool: {name}")
```

- Registers a single handler for all tool calls using `@server.call_tool()`
- Takes tool name and parameters as input
- Generates a unique request ID for each tool call
- Logs the tool call with parameters
- Dispatches to the appropriate tool implementation based on name
- Returns results wrapped in a list of TextContent objects
- Raises an exception for unknown tool names

## Address Objects Tool Implementation

```python
async def retrieve_address_objects(params: Dict, request_id: str) -> TextContent:
    """
    Retrieve address objects from the firewall.

    Args:
        params: Tool parameters including location and vsys
        request_id: Unique request identifier

    Returns:
        TextContent containing JSON string of address objects
    """
    try:
        # Validate inputs
        if "location" not in params:
            raise ValueError("Missing required parameter: location")
        if "vsys" not in params:
            raise ValueError("Missing required parameter: vsys")

        location = params.get("location")
        vsys = params.get("vsys")

        # Call Palo Alto API
        logger.debug(f"Calling get_address_objects with location={location}, vsys={vsys}")
        address_objects = await get_address_objects(location, vsys)
        logger.debug(f"Received address_objects from API: {address_objects}")

        # Format result as JSON string
        result = json.dumps(address_objects, indent=2)
        logger.debug(f"Formatted JSON result: {result[:500]}...")

        logger.info(
            json.dumps(
                {
                    "request_id": request_id,
                    "message": "Successfully retrieved address objects",
                    "count": len(address_objects),
                }
            )
        )

        # Create TextContent response for MCP
        response = TextContent(result)
        logger.debug(f"Created TextContent response with type: {type(response)}, content_type: {response.content_type}")

        return response

    except (ValueError, PaloAltoApiError) as e:
        logger.error(json.dumps({"request_id": request_id, "message": f"Error retrieving address objects: {str(e)}"}))
        return TextContent(json.dumps({"error": str(e)}))
```

- Implements the `retrieve_address_objects` tool
- Validates that required parameters are present
- Extracts location and vsys parameters
- Calls the Palo Alto API function to get address objects
- Formats the result as a nicely indented JSON string
- Logs success with the number of objects retrieved
- Creates a TextContent response with the JSON string
- Handles both ValueError and PaloAltoApiError exceptions
- Returns error information as a structured JSON string within TextContent

## Security Zones Tool Implementation

```python
async def retrieve_security_zones(params: Dict, request_id: str) -> TextContent:
    """
    Retrieve security zones from the firewall.

    Args:
        params: Tool parameters including location and vsys
        request_id: Unique request identifier

    Returns:
        TextContent containing JSON string of security zones
    """
```

- Similar implementation pattern to retrieve_address_objects
- Validates parameters, calls the API, formats the result
- Returns security zones information as TextContent

## Security Policies Tool Implementation

```python
async def retrieve_security_policies(params: Dict, request_id: str) -> TextContent:
    """
    Retrieve security policies from the firewall.

    Args:
        params: Tool parameters including location and vsys
        request_id: Unique request identifier

    Returns:
        TextContent containing JSON string of security policies
    """
```

- Similar implementation pattern to the other tools
- Validates parameters, calls the API, formats the result
- Returns security policy information as TextContent
