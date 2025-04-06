#!/bin/bash
# Script to run the MCP server with HTTP transport

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if PANOS_HOSTNAME and PANOS_API_KEY are set
if [ -z "$PANOS_HOSTNAME" ] || [ -z "$PANOS_API_KEY" ]; then
    echo "Error: PANOS_HOSTNAME and PANOS_API_KEY environment variables must be set."
    echo "You can set them by running:"
    echo "export PANOS_HOSTNAME=your-firewall-hostname"
    echo "export PANOS_API_KEY=your-api-key"
    exit 1
fi

# Set environment variables for HTTP transport
export MCP_TRANSPORT=http
export MCP_HTTP_HOST=localhost
export MCP_HTTP_PORT=8000

echo "Starting MCP server with HTTP transport..."
echo "PANOS_HOSTNAME: $PANOS_HOSTNAME"
echo "PANOS_DEBUG: $PANOS_DEBUG"
echo "Server will be available at: http://localhost:8000"

# Run the server using Poetry
poetry run python -m palo_alto_mcp
