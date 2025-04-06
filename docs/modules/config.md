# Configuration Module

The configuration module (`config.py`) is responsible for loading and validating the application settings from environment variables.

## Settings Class

```python
class Settings(BaseSettings):
    """Settings for the Palo Alto Networks MCP Server.

    Attributes:
        panos_hostname: Hostname or IP address of the Palo Alto Networks NGFW.
        panos_api_key: API key for authenticating with the Palo Alto Networks NGFW.
        debug: Enable debug logging.
    """

    panos_hostname: str
    panos_api_key: str
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Using the correct prefix for environment variables
        # This ensures PANOS_HOSTNAME maps to panos_hostname
        env_prefix="PANOS_",
        case_sensitive=False,
    )
```

The `Settings` class is a Pydantic model that defines the application settings. It uses `pydantic-settings` to load values from environment variables with the following features:

- Loads settings from environment variables with the `PANOS_` prefix
- Supports loading from a `.env` file in the project root
- Case-insensitive environment variable names
- Type validation for all settings

## get_settings Function

```python
def get_settings() -> Settings:
    """Get the application settings from environment variables.

    Returns:
        Settings object with configuration values.

    Raises:
        ValueError: If required environment variables are missing.
    """
    try:
        # Get values from environment variables directly to satisfy type checker
        hostname = os.environ.get("PANOS_HOSTNAME")
        api_key = os.environ.get("PANOS_API_KEY")

        # Get debug flag from environment variable
        debug_str = os.environ.get("PANOS_DEBUG", "false").lower()
        debug = debug_str in ("true", "1", "yes", "y", "on")

        # Create Settings with explicit values to satisfy type checker
        if hostname and api_key:
            return Settings(panos_hostname=hostname, panos_api_key=api_key, debug=debug)
        
        # If any required values are missing, try loading from .env file
        settings = Settings()
        return settings
    except Exception as e:
        # Provide a helpful error message
        error_msg = f"Failed to load settings: {str(e)}"
        required_vars = ["PANOS_HOSTNAME", "PANOS_API_KEY"]
        missing_vars = [var for var in required_vars if os.environ.get(var) is None]
        
        if missing_vars:
            error_msg += f"\nMissing required environment variables: {', '.join(missing_vars)}"
            error_msg += "\nPlease set these variables in your environment or .env file."
        
        raise ValueError(error_msg) from e
```

The `get_settings` function attempts to load the application settings from environment variables. If the required environment variables are missing, it provides a helpful error message indicating which variables need to be set.

## Environment Variables

The configuration module uses the following environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `PANOS_HOSTNAME` | Hostname or IP address of the Palo Alto Networks NGFW | Yes | None |
| `PANOS_API_KEY` | API key for authenticating with the Palo Alto Networks NGFW | Yes | None |
| `PANOS_DEBUG` | Enable debug logging | No | `false` |

## .env File Support

The configuration module supports loading settings from a `.env` file in the project root directory. This file should contain key-value pairs in the format:

```
PANOS_HOSTNAME=firewall.example.com
PANOS_API_KEY=your-api-key
PANOS_DEBUG=false
```

!!! warning
    Never commit the `.env` file to version control as it contains sensitive information.

## Example Usage

```python
from palo_alto_mcp.config import get_settings

def example():
    try:
        settings = get_settings()
        print(f"Hostname: {settings.panos_hostname}")
        print(f"Debug mode: {settings.debug}")
    except ValueError as e:
        print(f"Configuration error: {str(e)}")
