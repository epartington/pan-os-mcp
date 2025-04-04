"""
MCP Tools Module

This module defines the MCP tools for interacting with Palo Alto Networks devices.
"""

import json
import logging
import uuid
from typing import Dict, List

import mcp
from mcp.server import Server
from mcp.types import TextContent

from palo_alto_api import PaloAltoApiError, get_address_objects, get_security_policies, get_security_zones

# Configure logging
logger = logging.getLogger("mcp-paloalto.tools")

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


def register_tools(server: Server) -> None:
    """Register all tools with the MCP server."""

    # Register list_tools handler
    @server.list_tools()
    async def handle_list_tools():
        """Return the list of available tools."""
        request_id = str(uuid.uuid4())
        logger.info(json.dumps({"request_id": request_id, "message": "Listing available tools"}))
        return await list_tools()

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

    # Define the actual tool implementation functions
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

    async def retrieve_security_zones(params: Dict, request_id: str) -> TextContent:
        """
        Retrieve security zones from the firewall.

        Args:
            params: Tool parameters including location and vsys
            request_id: Unique request identifier

        Returns:
            TextContent containing JSON string of security zones
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
            security_zones = await get_security_zones(location, vsys)

            # Format result as JSON string
            result = json.dumps(security_zones, indent=2)
            logger.info(
                json.dumps(
                    {"request_id": request_id, "message": "Successfully retrieved security zones", "count": len(security_zones)}
                )
            )

            return TextContent(result)

        except (ValueError, PaloAltoApiError) as e:
            logger.error(json.dumps({"request_id": request_id, "message": f"Error retrieving security zones: {str(e)}"}))
            return TextContent(json.dumps({"error": str(e)}))

    async def retrieve_security_policies(params: Dict, request_id: str) -> TextContent:
        """
        Retrieve security policies from the firewall.

        Args:
            params: Tool parameters including location and vsys
            request_id: Unique request identifier

        Returns:
            TextContent containing JSON string of security policies
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
            security_policies = await get_security_policies(location, vsys)

            # Format result as JSON string
            result = json.dumps(security_policies, indent=2)
            logger.info(
                json.dumps(
                    {
                        "request_id": request_id,
                        "message": "Successfully retrieved security policies",
                        "count": len(security_policies),
                    }
                )
            )

            return TextContent(result)

        except (ValueError, PaloAltoApiError) as e:
            logger.error(json.dumps({"request_id": request_id, "message": f"Error retrieving security policies: {str(e)}"}))
            return TextContent(json.dumps({"error": str(e)}))

    # The tools_list handler is no longer needed since we're setting server.list_tools_handler in main.py
    # Instead, we'll use the global list_tools function directly
