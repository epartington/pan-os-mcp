#!/bin/bash
# Script to run the MCP server with environment variables from .env file

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found."
    echo "Please create a .env file with the following content:"
    echo "PANOS_HOSTNAME=your-firewall-hostname"
    echo "PANOS_API_KEY=your-api-key"
    echo "PANOS_DEBUG=true|false"
    exit 1
fi

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

echo "Starting MCP server with environment variables from .env file..."
echo "PANOS_HOSTNAME: $PANOS_HOSTNAME"
echo "PANOS_DEBUG: $PANOS_DEBUG"

# Run the server using Poetry
poetry run python -m palo_alto_mcp
