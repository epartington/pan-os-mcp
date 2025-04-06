# Configuration

The Palo Alto Networks MCP Server is configured primarily through environment variables.

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `PANOS_HOSTNAME` | Hostname or IP address of the Palo Alto Networks NGFW |
| `PANOS_API_KEY` | API key for authenticating with the Palo Alto Networks NGFW |

## Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PANOS_DEBUG` | Enable debug logging | `false` |

## Configuration Methods

### Using .env File

You can create a `.env` file in the root directory of the project with the following content:

```
PANOS_HOSTNAME=firewall.example.com
PANOS_API_KEY=your-api-key
PANOS_DEBUG=false
```

!!! warning
    Never commit the `.env` file to version control as it contains sensitive information.

### Setting Environment Variables Directly

#### On Linux/macOS

```bash
export PANOS_HOSTNAME=firewall.example.com
export PANOS_API_KEY=your-api-key
export PANOS_DEBUG=false
```

#### On Windows (Command Prompt)

```cmd
set PANOS_HOSTNAME=firewall.example.com
set PANOS_API_KEY=your-api-key
set PANOS_DEBUG=false
```

#### On Windows (PowerShell)

```powershell
$env:PANOS_HOSTNAME = "firewall.example.com"
$env:PANOS_API_KEY = "your-api-key"
$env:PANOS_DEBUG = "false"
```

## Obtaining an API Key

To obtain an API key from your Palo Alto Networks firewall:

1. Log in to the web interface of your Palo Alto Networks firewall.
2. Navigate to **Device** > **Users** > **API Key Generation**.
3. Click **Generate API Key**.
4. Copy the generated API key and use it as the value for the `PANOS_API_KEY` environment variable.

!!! note
    API keys are associated with the user account that generates them and inherit the permissions of that user. Make sure the user has sufficient permissions to access the data you need.

## HTTP Server Configuration

When running the MCP server with HTTP transport (for development or testing), you can use the provided script:

```bash
./scripts/run_http_server.sh
```

This script sets the necessary environment variables and starts the server with HTTP transport enabled.

## Windsurf Integration

To configure the server for use with Windsurf, you need to update the `mcp_config.json` file in your Windsurf configuration directory:

```json
{
  "command": "python",
  "args": ["-m", "palo_alto_mcp"],
  "env": {
    "PANOS_HOSTNAME": "firewall.example.com",
    "PANOS_API_KEY": "your-api-key"
  }
}
```

Make sure to replace the placeholder values with your actual firewall hostname and API key.
