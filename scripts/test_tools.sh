#!/bin/bash
# Script to test the MCP server tools using the mcp CLI

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

echo "Testing MCP server tools..."

# Start the server in the background
echo "Starting MCP server in the background..."
poetry run python -m palo_alto_mcp &
SERVER_PID=$!

# Give the server some time to start
sleep 2

# Test the tools
echo "Testing show_system_info tool..."
mcp call-tool --command "python -m palo_alto_mcp" --tool show_system_info

echo "Testing retrieve_address_objects tool..."
mcp call-tool --command "python -m palo_alto_mcp" --tool retrieve_address_objects

echo "Testing retrieve_security_zones tool..."
mcp call-tool --command "python -m palo_alto_mcp" --tool retrieve_security_zones

echo "Testing retrieve_security_policies tool..."
mcp call-tool --command "python -m palo_alto_mcp" --tool retrieve_security_policies

# Kill the server
echo "Stopping MCP server..."
kill $SERVER_PID

echo "All tests completed."
