# Basic Usage

This guide covers how to use the Palo Alto Networks MCP Server.

## Starting the Server

After installation, you can start the server using the following command:

```bash
python -m palo_alto_mcp
```

This will start the MCP server using standard I/O transport, which is suitable for command-based execution by MCP clients like Windsurf.

## Available Tools

The server provides the following tools:

### show_system_info

Retrieves system information from the Palo Alto Networks firewall.

**Example output:**

```
# Palo Alto Networks Firewall System Information

**hostname**: fw01.example.com
**model**: PA-3260
**serial**: 001234567890
**sw-version**: 10.1.6-h3
**uptime**: 63 days, 12:34:56
```

### retrieve_address_objects

Retrieves address objects configured on the Palo Alto Networks firewall.

**Example output:**

```
# Palo Alto Networks Firewall Address Objects

## internal-subnet
- **Type**: ip-netmask
- **Value**: 10.0.0.0/24
- **Description**: Internal network

## web-server
- **Type**: ip-netmask
- **Value**: 10.0.0.10/32
- **Description**: Web server
```

### retrieve_security_zones

Retrieves security zones configured on the Palo Alto Networks firewall.

**Example output:**

```
# Palo Alto Networks Firewall Security Zones

## trust
- **Type**: layer3
- **Interfaces**:
  - ethernet1/1
  - ethernet1/2

## untrust
- **Type**: layer3
- **Interfaces**:
  - ethernet1/3
```

### retrieve_security_policies

Retrieves security policies configured on the Palo Alto Networks firewall.

**Example output:**

```
# Palo Alto Networks Firewall Security Policies

## allow-outbound
- **Description**: Allow outbound traffic
- **Action**: allow
- **Source Zones**:
  - trust
- **Source Addresses**:
  - any
- **Destination Zones**:
  - untrust
- **Destination Addresses**:
  - any
- **Applications**:
  - web-browsing
  - ssl
- **Services**:
  - application-default
```

## Integration with MCP Clients

This server is designed to be used with MCP clients like Windsurf. The client will need to be configured to use the command-based execution pattern, specifying the command to run the server.

For example, in a client configuration:

```json
{
  "command": "python",
  "args": ["-m", "palo_alto_mcp"]
}
```

The server uses the standard I/O transport mechanism for communication with the client, which is automatically handled by the `modelcontextprotocol` SDK.
