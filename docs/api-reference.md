# Palo Alto MCP Server API Reference

This document provides a detailed reference for all tools available in the Palo Alto MCP server, including their parameters, response formats, and examples.

## Protocol Overview

The Palo Alto MCP server implements the Model Context Protocol (MCP), supporting the following core operations:

- `list_tools`: Retrieves a list of available tools
- `call_tool`: Executes a specific tool with parameters

All requests and responses use JSON format and follow the JSON-RPC 2.0 specification.

## Available Tools

### retrieve_address_objects

Retrieves address objects from a Palo Alto Networks firewall.

#### Parameters

| Parameter | Type   | Required | Default | Description                           |
|-----------|--------|----------|---------|---------------------------------------|
| location  | string | Yes      | -       | Hostname or IP address of the firewall |
| vsys      | string | No       | vsys1   | Virtual system name                   |

#### Response Format

```json
{
  "toolResult": {
    "content": [
      {
        "type": "text",
        "text": "[
          {
            \"name\": \"web-server\",
            \"ip-netmask\": \"10.0.1.100/32\",
            \"description\": \"Primary web server\",
            \"tags\": [\"production\", \"web\"]
          },
          {
            \"name\": \"internal-network\",
            \"ip-netmask\": \"192.168.1.0/24\",
            \"description\": \"Internal network\",
            \"tags\": [\"internal\"]
          }
        ]"
      }
    ]
  }
}
```

#### Example

```javascript
// Request
{
  "jsonrpc": "2.0",
  "method": "call_tool",
  "id": "1",
  "params": {
    "name": "retrieve_address_objects",
    "parameters": {
      "location": "10.1.1.1",
      "vsys": "vsys1"
    }
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "toolResult": {
      "content": [
        {
          "type": "text",
          "text": "[{\"name\":\"web-server\",...}]"
        }
      ]
    }
  }
}
```

### retrieve_security_zones

Retrieves security zones from a Palo Alto Networks firewall.

#### Parameters

| Parameter | Type   | Required | Default | Description                           |
|-----------|--------|----------|---------|---------------------------------------|
| location  | string | Yes      | -       | Hostname or IP address of the firewall |
| vsys      | string | No       | vsys1   | Virtual system name                   |

#### Response Format

```json
{
  "toolResult": {
    "content": [
      {
        "type": "text",
        "text": "[
          {
            \"name\": \"trust\",
            \"interfaces\": [\"ethernet1/1\", \"ethernet1/2\"]
          },
          {
            \"name\": \"untrust\",
            \"interfaces\": [\"ethernet1/3\"]
          }
        ]"
      }
    ]
  }
}
```

#### Example

```javascript
// Request
{
  "jsonrpc": "2.0",
  "method": "call_tool",
  "id": "2",
  "params": {
    "name": "retrieve_security_zones",
    "parameters": {
      "location": "10.1.1.1",
      "vsys": "vsys1"
    }
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": "2",
  "result": {
    "toolResult": {
      "content": [
        {
          "type": "text",
          "text": "[{\"name\":\"trust\",...}]"
        }
      ]
    }
  }
}
```

### retrieve_security_policies

Retrieves security policies from a Palo Alto Networks firewall.

#### Parameters

| Parameter | Type   | Required | Default | Description                           |
|-----------|--------|----------|---------|---------------------------------------|
| location  | string | Yes      | -       | Hostname or IP address of the firewall |
| vsys      | string | No       | vsys1   | Virtual system name                   |

#### Response Format

```json
{
  "toolResult": {
    "content": [
      {
        "type": "text",
        "text": "[
          {
            \"name\": \"allow-web\",
            \"source_zones\": [\"untrust\"],
            \"destination_zones\": [\"trust\"],
            \"source_addresses\": [\"any\"],
            \"destination_addresses\": [\"web-server\"],
            \"applications\": [\"web-browsing\", \"ssl\"],
            \"services\": [\"application-default\"],
            \"action\": \"allow\"
          },
          {
            \"name\": \"block-all\",
            \"source_zones\": [\"untrust\"],
            \"destination_zones\": [\"trust\"],
            \"source_addresses\": [\"any\"],
            \"destination_addresses\": [\"any\"],
            \"applications\": [\"any\"],
            \"services\": [\"any\"],
            \"action\": \"deny\"
          }
        ]"
      }
    ]
  }
}
```

#### Example

```javascript
// Request
{
  "jsonrpc": "2.0",
  "method": "call_tool",
  "id": "3",
  "params": {
    "name": "retrieve_security_policies",
    "parameters": {
      "location": "10.1.1.1",
      "vsys": "vsys1"
    }
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": "3",
  "result": {
    "toolResult": {
      "content": [
        {
          "type": "text",
          "text": "[{\"name\":\"allow-web\",...}]"
        }
      ]
    }
  }
}
```

## Error Handling

The server returns standard JSON-RPC error responses with these common error cases:

### Missing Required Parameters

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "error": {
    "code": -32602,
    "message": "Invalid params: location parameter is required"
  }
}
```

### Unknown Tool

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "error": {
    "code": -32601,
    "message": "Unknown tool: nonexistent_tool"
  }
}
```

### API Authentication Error

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "toolResult": {
      "content": [
        {
          "type": "text",
          "text": "Error: PAN-OS API error: API key authentication failed"
        }
      ],
      "isError": true
    }
  }
}
```

### Connection Error

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "toolResult": {
      "content": [
        {
          "type": "text",
          "text": "Error: PAN-OS API request failed: Unable to connect to firewall"
        }
      ],
      "isError": true
    }
  }
}
```

## Tool Response Schema

All successful tool executions return a response following this general structure:

```typescript
interface ToolResponse {
  jsonrpc: "2.0";
  id: string;
  result: {
    toolResult: {
      content: Array<{
        type: "text";
        text: string; // JSON-formatted string
      }>;
      isError?: boolean; // Present and true for error responses
    }
  }
}
```

## Implementation Notes

1. The `text` field in the tool response contains a JSON-formatted string that needs to be parsed by the client.
2. All API responses are formatted for readability with consistent field naming.
3. API responses that contain empty collections will return an empty array `[]` instead of null.
4. The server applies proper escaping to ensure the JSON response is valid.
