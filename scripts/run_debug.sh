#!/bin/bash
# Script to run the MCP server in debug mode

# Set environment variables for debug mode
export PANOS_DEBUG=true

# Check if PANOS_HOSTNAME and PANOS_API_KEY are set
if [ -z "$PANOS_HOSTNAME" ] || [ -z "$PANOS_API_KEY" ]; then
    echo "Error: PANOS_HOSTNAME and PANOS_API_KEY environment variables must be set."
    echo "You can set them by running:"
    echo "export PANOS_HOSTNAME=your-firewall-hostname"
    echo "export PANOS_API_KEY=your-api-key"
    exit 1
fi

echo "Starting MCP server in debug mode..."
echo "PANOS_HOSTNAME: $PANOS_HOSTNAME"
echo "PANOS_DEBUG: $PANOS_DEBUG"

# Run the server using Poetry
poetry run python -m palo_alto_mcp
