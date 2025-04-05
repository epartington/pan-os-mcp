# Palo Alto MCP Server

A TypeScript-based Model Context Protocol (MCP) server for integrating with Palo Alto Networks Next-Generation Firewall (NGFW) appliances. This server enables Windsurf and other MCP clients to retrieve firewall configuration data through simple tool calls.

## Features

- TypeScript implementation following the Cloudflare MCP server pattern
- Retrieval of address objects, security zones, and security policies from Palo Alto firewalls
- Support for standard I/O transport for command-line integration
- npm package for easy installation and execution

## Installation

```bash
# Install globally
npm install -g palo-alto-mcp

# Or run without installing
npx -y palo-alto-mcp
```

## Configuration

The server requires the following environment variables:

```bash
# API key for authentication with Palo Alto firewall
export PALO_ALTO_API_KEY="your-api-key-here"

# Base URL for the Palo Alto API (include /api at the end)
export PALO_ALTO_API_URL="https://your-firewall-ip-or-hostname/api"

# Optional: Enable detailed logging
export DEBUG="true"
```

### Initialization

To set up a configuration file:

```bash
npx -y palo-alto-mcp init
```

This creates a configuration template at `~/.palo-alto-mcp/config.json`.

## Integration with Windsurf

Add this to your `mcp_config.json` file:

```json
{
  "palo-alto": {
    "command": "npx -y palo-alto-mcp",
    "args": []
  }
}
```

Make sure the environment variables are properly set before starting Windsurf.

## Available Tools

| Tool Name | Description | Required Parameters |
|-----------|-------------|---------------------|
| `retrieve_address_objects` | Retrieve address objects from a Palo Alto firewall | `location` (firewall hostname/IP), `vsys` (default: vsys1) |
| `retrieve_security_zones` | Retrieve security zones from a Palo Alto firewall | `location` (firewall hostname/IP), `vsys` (default: vsys1) |
| `retrieve_security_policies` | Retrieve security policies from a Palo Alto firewall | `location` (firewall hostname/IP), `vsys` (default: vsys1) |

## Usage Examples

### Retrieve Address Objects

```typescript
// Example call to retrieve address objects
const result = await callTool("retrieve_address_objects", {
  location: "10.1.1.1",
  vsys: "vsys1"
});
```

### Retrieve Security Zones

```typescript
// Example call to retrieve security zones
const result = await callTool("retrieve_security_zones", {
  location: "10.1.1.1",
  vsys: "vsys1"
});
```

### Retrieve Security Policies

```typescript
// Example call to retrieve security policies
const result = await callTool("retrieve_security_policies", {
  location: "10.1.1.1",
  vsys: "vsys1"
});
```

## Response Format

All tools return data in JSON format wrapped in a TextContent object per MCP specifications:

```json
{
  "toolResult": {
    "content": [
      {
        "type": "text",
        "text": "[JSON data for the requested objects]"
      }
    ]
  }
}
```

## Troubleshooting

### Common Errors

- **"API key is required"**: Ensure the `PALO_ALTO_API_KEY` environment variable is set
- **"API URL is required"**: Ensure the `PALO_ALTO_API_URL` environment variable is set
- **"PAN-OS API error"**: Check firewall connectivity and API permissions

### Debug Mode

Set `DEBUG=true` to enable detailed logging:

```bash
DEBUG=true npx -y palo-alto-mcp
```

### Logs

Logs use a structured JSON format with request IDs for easier tracking:

```json
{
  "timestamp": "2025-04-05T12:34:56.789Z",
  "request_id": "01234567-89ab-cdef-0123-456789abcdef",
  "message": "Making request to PAN-OS API: api"
}
```

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/palo-alto-mcp.git
cd palo-alto-mcp

# Install dependencies
npm install

# Build
npm run build

# Run in development mode
npm run dev

# Test
npm test
```

## License

MIT

## Project Patterns and Technology

- **TypeScript**: Strict typing with ES2022 target
- **MCP SDK**: Using `@modelcontextprotocol/sdk` for server implementation
- **HTTP Client**: `undici` for API requests
- **Validation**: `zod` for parameter validation
- **Transport**: Standard I/O transport for command-line execution
- **Environment**: Configuration via environment variables
- **Error Handling**: Structured error responses with clear messages
- **Logging**: Request ID-based logging with optional debug mode
