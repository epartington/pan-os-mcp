from fastapi import FastAPI, HTTPException

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
                    "vsys": {"type": "string", "default": "vsys1"}
                }
            },
            {
                "name": "retrieve_security_zones",
                "description": "Retrieve security zones from PAN-OS firewall",
                "parameters": {
                    "location": {"type": "string", "default": "vsys"},
                    "vsys": {"type": "string", "default": "vsys1"}
                }
            },
            {
                "name": "retrieve_security_policies",
                "description": "Retrieve security policies from PAN-OS firewall",
                "parameters": {
                    "location": {"type": "string", "default": "vsys"},
                    "vsys": {"type": "string", "default": "vsys1"}
                }
            }
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
            detail=(
                f"Invalid tool name. Available tools: "
                f"{', '.join(valid_tool_names)}"
            ),
        )
    
    # Apply default parameters if not provided
    tool_info = next(
        tool for tool in available_tools if tool["name"] == tool_name
    )
    for param_name, param_details in tool_info["parameters"].items():
        if param_name not in parameters and "default" in param_details:
            parameters[param_name] = param_details["default"]
    
    # Mock implementation - in a real scenario, this would make actual API calls
    # to the PAN-OS firewall
    mock_results = {
        "retrieve_address_objects": {
            "result": {"address-objects": []}, 
            "status": "success"
        },
        "retrieve_security_zones": {
            "result": {"zones": []}, 
            "status": "success"
        },
        "retrieve_security_policies": {
            "result": {"policies": []}, 
            "status": "success"
        },
    }
    
    return mock_results.get(
        tool_name, 
        {"status": "error", "message": "Tool execution failed"}
    )
