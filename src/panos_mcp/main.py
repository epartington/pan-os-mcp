import logging

from fastapi import FastAPI, HTTPException

from .config import settings
from .panos_api import PanOSClient

logger = logging.getLogger(__name__)

app = FastAPI(
    title="PAN-OS MCP Server",
    description="Management Control Plane server for Palo Alto Networks Firewalls",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the PAN-OS MCP Server!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/mcp/tools")
def get_available_tools():
    """Return the list of available tools and their parameters."""
    return {
        "tools": [
            {
                "name": "retrieve_address_objects",
                "description": "Retrieve address objects from PAN-OS firewall",
                "parameters": {
                    "location": {"type": "string", "default": "vsys"},
                    "vsys": {"type": "string", "default": "vsys1"},
                    "hostname": {"type": "string", "required": False},
                    "username": {"type": "string", "required": False},
                    "password": {"type": "string", "required": False},
                    "api_key": {"type": "string", "required": False},
                },
            },
            {
                "name": "retrieve_security_zones",
                "description": "Retrieve security zones from PAN-OS firewall",
                "parameters": {
                    "location": {"type": "string", "default": "vsys"},
                    "vsys": {"type": "string", "default": "vsys1"},
                    "hostname": {"type": "string", "required": False},
                    "username": {"type": "string", "required": False},
                    "password": {"type": "string", "required": False},
                    "api_key": {"type": "string", "required": False},
                },
            },
            {
                "name": "retrieve_security_policies",
                "description": "Retrieve security policies from PAN-OS firewall",
                "parameters": {
                    "location": {"type": "string", "default": "vsys"},
                    "vsys": {"type": "string", "default": "vsys1"},
                    "hostname": {"type": "string", "required": False},
                    "username": {"type": "string", "required": False},
                    "password": {"type": "string", "required": False},
                    "api_key": {"type": "string", "required": False},
                },
            },
        ]
    }


@app.post("/mcp/execute")
async def execute_tool(request: dict):
    """Execute a specific tool with the provided parameters."""
    # Validate request format
    if "tool" not in request or "parameters" not in request:
        raise HTTPException(
            status_code=400,
            detail="Request must include 'tool' and 'parameters' fields",
        )

    tool_name = request.get("tool")
    parameters = request.get("parameters", {})

    # Validate tool name
    available_tools = get_available_tools()["tools"]
    valid_tool_names = [tool["name"] for tool in available_tools]

    if tool_name not in valid_tool_names:
        raise HTTPException(
            status_code=400,
            detail=(f"Invalid tool name. Available tools: {', '.join(valid_tool_names)}"),
        )

    # Apply default parameters if not provided
    tool_info = next(tool for tool in available_tools if tool["name"] == tool_name)
    for param_name, param_details in tool_info["parameters"].items():
        if param_name not in parameters and "default" in param_details:
            parameters[param_name] = param_details["default"]

    # Get authentication parameters
    hostname = parameters.get("hostname", settings.panos_hostname)
    username = parameters.get("username", settings.panos_username)
    password = parameters.get("password", settings.panos_password)
    api_key = parameters.get("api_key", settings.panos_api_key)
    verify_ssl = settings.panos_verify_ssl

    # Validate that we have sufficient authentication parameters
    if not hostname:
        raise HTTPException(
            status_code=400,
            detail="Firewall hostname is required",
        )

    if not api_key and not (username and password):
        raise HTTPException(
            status_code=400,
            detail="API key or username and password are required",
        )

    try:
        # Initialize PAN-OS client
        client = PanOSClient(
            hostname=hostname,
            username=username,
            password=password,
            api_key=api_key,
            verify_ssl=verify_ssl,
        )

        # Execute the requested tool
        if tool_name == "retrieve_security_policies":
            location = parameters.get("location", "vsys")
            vsys = parameters.get("vsys", "vsys1")
            result = client.get_security_policies(location=location, vsys=vsys)
            return {"result": result, "status": "success"}

        # For other tools (implement these when needed)
        elif tool_name == "retrieve_address_objects":
            # Mock implementation for now
            return {"result": {"address-objects": []}, "status": "success"}

        elif tool_name == "retrieve_security_zones":
            # Mock implementation for now
            return {"result": {"zones": []}, "status": "success"}

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tool implementation for {tool_name} not found",
            )

    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        return {"status": "error", "message": f"Tool execution failed: {str(e)}"}
