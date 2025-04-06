#!/bin/bash
# Script to run the MCP server with MCP Inspector for interactive testing

# Check if PANOS_HOSTNAME and PANOS_API_KEY are set
if [ -z "$PANOS_HOSTNAME" ] || [ -z "$PANOS_API_KEY" ]; then
    echo "Error: PANOS_HOSTNAME and PANOS_API_KEY environment variables must be set."
    echo "You can set them by running:"
    echo "export PANOS_HOSTNAME=your-firewall-hostname"
    echo "export PANOS_API_KEY=your-api-key"
    exit 1
fi

# Check if mcp CLI is installed
if ! command -v mcp &> /dev/null; then
    echo "Error: mcp CLI not found. Please install it with:"
    echo "pip install modelcontextprotocol"
    exit 1
fi

echo "Starting MCP server with MCP Inspector..."
echo "PANOS_HOSTNAME: $PANOS_HOSTNAME"

# Run the server with MCP Inspector
poetry run mcp dev --command "python -m palo_alto_mcp"
