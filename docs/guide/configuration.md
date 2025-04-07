# Configuration

The Palo Alto Networks MCP Server is configured primarily through environment variables.

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `PANOS_HOSTNAME` | Hostname or IP address of the Palo Alto Networks NGFW or Panorama |
| `PANOS_API_KEY` | API key for authenticating with the Palo Alto Networks NGFW or Panorama |

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

To obtain an API key from your Palo Alto Networks firewall or Panorama:

1. Log in to the web interface of your Palo Alto Networks firewall or Panorama.
2. Navigate to **Device** > **Users** > **API Key Generation**.
3. Click **Generate API Key**.
4. Copy the generated API key and use it as the value for the `PANOS_API_KEY` environment variable.

!!! note
    API keys are associated with the user account that generates them and inherit the permissions of that user. Make sure the user has sufficient permissions to access the data you need.

### Programmatic API Key Generation

You can also generate an API key programmatically using the included script:

```bash
python -m scripts.generate_api_key --hostname firewall.example.com --username admin --password "your-password"
```

This script will authenticate with the firewall or Panorama and generate an API key that you can use in your configuration.

## HTTP Server Configuration

When running the MCP server with HTTP transport (for development or testing), you can use the provided script:

```bash
./scripts/run_http_server.sh
```

This script sets the necessary environment variables and starts the server with HTTP transport enabled.

## Panorama vs. Firewall Configuration

The MCP server automatically detects whether it's connecting to a Panorama management platform or a standalone firewall:

- When connected to **Panorama**, the server will retrieve device groups and organize address objects hierarchically by device group.
- When connected to a **standalone firewall**, the server will retrieve address objects from the vsys configuration.

No additional configuration is needed to switch between Panorama and firewall mode - the server will detect the device type automatically.

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

Make sure to replace the placeholder values with your actual firewall or Panorama hostname and API key.
