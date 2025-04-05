# Connecting Clients to the Palo Alto MCP Server

This document provides comprehensive guidance on how to connect different clients to the Palo Alto MCP server, with a particular focus on the Windsurf client integration.

## Overview

The Palo Alto MCP server follows the Model Context Protocol (MCP) standard, allowing it to connect with any compatible MCP client. This guide focuses on connecting the server with:

1. Windsurf MCP client (primary use case)
2. Generic MCP clients
3. Custom implementations

## Prerequisites

Before connecting a client, ensure you have:

1. Installed the Palo Alto MCP server (`npm install -g palo-alto-mcp`)
2. Access to a Palo Alto Networks firewall
3. A valid API key for the firewall
4. Network connectivity to the firewall

## Windsurf MCP Client Integration

### Configuration Setup

The Windsurf client uses an `mcp_config.json` file to manage its MCP server connections. To connect to the Palo Alto MCP server:

1. Locate your Windsurf configuration directory
2. Open or create the `mcp_config.json` file
3. Add the Palo Alto MCP server configuration

```json
{
  "palo-alto": {
    "command": "npx -y palo-alto-mcp",
    "args": []
  }
}
```

> **IMPORTANT**: According to the MCP server pattern requirements, ensure the message endpoints are correctly set up with `/sse` for the main SSE connection endpoint and `/messages/` (not `/sse-messages/`) for the message endpoint.

### Environment Variables Setup

Set the required environment variables before starting Windsurf:

```bash
# Bash/Zsh
export PALO_ALTO_API_KEY="your-api-key-here"
export PALO_ALTO_API_URL="https://your-firewall-ip-or-hostname/api"
export DEBUG="true"  # Optional, for verbose logging

# Windows Command Prompt
set PALO_ALTO_API_KEY=your-api-key-here
set PALO_ALTO_API_URL=https://your-firewall-ip-or-hostname/api
set DEBUG=true

# Windows PowerShell
$env:PALO_ALTO_API_KEY="your-api-key-here"
$env:PALO_ALTO_API_URL="https://your-firewall-ip-or-hostname/api"
$env:DEBUG="true"
```

### Tool Usage in Windsurf

Once connected, you can call the Palo Alto MCP tools from Windsurf:

1. List available tools to verify connection:
   ```typescript
   const tools = await client.listTools();
   console.log(tools);
   ```

2. Call a specific tool:
   ```typescript
   const result = await client.callTool("retrieve_address_objects", {
     location: "10.1.1.1",
     vsys: "vsys1"
   });
   console.log(result);
   ```

## Generic MCP Client Integration

For other MCP clients that follow the protocol specification:

### Direct Command Execution

Most MCP clients support executing external commands:

```
command: npx -y palo-alto-mcp
```

### Standard I/O Communication

The Palo Alto MCP server uses standard I/O transport, so ensure your client is configured to communicate via this method.

### Protocol Compatibility

Ensure your client implements:
- `list_tools` request handling
- `call_tool` request handling
- Proper parsing of TextContent responses

## Custom Client Implementation

If you're implementing a custom client to connect to the Palo Alto MCP server:

### Basic Connection Flow

1. **Start the Server Process**:
   ```javascript
   const { spawn } = require('child_process');
   const server = spawn('npx', ['-y', 'palo-alto-mcp']);
   ```

2. **Send List Tools Request**:
   ```javascript
   const listToolsRequest = {
     jsonrpc: '2.0',
     method: 'list_tools',
     id: '1',
     params: {}
   };
   server.stdin.write(JSON.stringify(listToolsRequest) + '\n');
   ```

3. **Send Call Tool Request**:
   ```javascript
   const callToolRequest = {
     jsonrpc: '2.0',
     method: 'call_tool',
     id: '2',
     params: {
       name: 'retrieve_address_objects',
       parameters: {
         location: '10.1.1.1',
         vsys: 'vsys1'
       }
     }
   };
   server.stdin.write(JSON.stringify(callToolRequest) + '\n');
   ```

4. **Process Responses**:
   ```javascript
   server.stdout.on('data', (data) => {
     const responses = data.toString().trim().split('\n');
     for (const response of responses) {
       const parsedResponse = JSON.parse(response);
       // Handle response based on id or method
     }
   });
   ```

### Error Handling

Ensure your client properly handles error responses:

```javascript
if (parsedResponse.error) {
  console.error('MCP Error:', parsedResponse.error);
  // Handle appropriately
}
```

## Troubleshooting Client Connections

### Common Connection Issues

1. **"Cannot find module 'palo-alto-mcp'"**:
   - Solution: Install the package globally: `npm install -g palo-alto-mcp`

2. **"API key is required"**:
   - Solution: Set the `PALO_ALTO_API_KEY` environment variable

3. **"API URL is required"**:
   - Solution: Set the `PALO_ALTO_API_URL` environment variable

4. **No response from server**:
   - Check if the server process started correctly
   - Verify environment variables are set in the right scope
   - Check for firewall or network connectivity issues

### Debugging Client-Server Communication

1. **Enable Debug Mode**:
   ```bash
   DEBUG=true npx -y palo-alto-mcp
   ```

2. **Inspect Standard Error**:
   The server logs to stderr, so capture and inspect these logs:
   ```bash
   npx -y palo-alto-mcp 2> palo-alto-mcp.log
   ```

3. **Test with Direct Commands**:
   Test basic functionality without a client:
   ```bash
   echo '{"jsonrpc":"2.0","method":"list_tools","id":"1","params":{}}' | npx -y palo-alto-mcp
   ```

## Security Considerations for Client Integration

1. **API Key Protection**:
   - Use environment variables instead of hardcoding API keys
   - Consider using credential stores or secret management systems

2. **Network Security**:
   - Ensure the client has secure connectivity to the firewall
   - Use HTTPS for all communication with the Palo Alto API

3. **Access Control**:
   - Use a specific API key with limited permissions
   - Follow the principle of least privilege

## Performance Optimization

1. **Connection Reuse**:
   - Keep the MCP server running for multiple requests
   - Avoid starting a new process for each tool call

2. **Parallel Processing**:
   - The server handles one request at a time
   - For batch processing, consider multiple server instances

## Advanced Configuration

### Custom Tool Parameters

You can extend the default tool parameters based on your needs:

```javascript
// Example with additional parameters
const result = await client.callTool("retrieve_address_objects", {
  location: "10.1.1.1",
  vsys: "vsys1",
  // Additional parameters could be added here if the tool implementation is extended
});
```

### Environment Configuration

For production environments, consider using a `.env` file or system environment variables to manage configuration:

```bash
# .env file example
PALO_ALTO_API_KEY=your-api-key-here
PALO_ALTO_API_URL=https://your-firewall-ip-or-hostname/api
DEBUG=false
```

Then use a package like `dotenv` in your client application to load these variables.
