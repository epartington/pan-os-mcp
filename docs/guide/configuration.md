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

## Obtaining a Palo Alto Networks API Key

1. Log in to the Palo Alto Networks web interface
2. Navigate to Device > Users > Local User Management
3. Select the user and click "Generate API Key"
4. Copy the generated API key

!!! note
    The API key provides access to your firewall with the same permissions as the user account. Use a dedicated account with appropriate permissions for security.
