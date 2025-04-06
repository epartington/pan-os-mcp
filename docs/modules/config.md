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

The `Settings` class is a Pydantic model that defines the application settings. It uses `pydantic-settings` to load values from environment variables.

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
            return Settings(
                panos_hostname=hostname,
                panos_api_key=api_key,
                debug=debug
            )

        # If environment variables are not set, let Pydantic handle validation
        # This will raise appropriate validation errors
        settings = Settings(
            # Type ignore to bypass type checker - Pydantic will handle validation
            panos_hostname=hostname or "",  # type: ignore
            panos_api_key=api_key or "",  # type: ignore
            debug=debug
        )
        return settings
    except Exception as e:
        error_msg = (
            f"Error loading configuration: {str(e)}\n"
            "Please ensure the following environment variables are set:\n"
            "- PANOS_HOSTNAME: Hostname or IP address of the Palo Alto Networks NGFW\n"
            "- PANOS_API_KEY: API key for authenticating with the Palo Alto Networks NGFW\n"
            "Optional environment variables:\n"
            "- PANOS_DEBUG: Set to 'true' to enable debug logging"
        )
        raise ValueError(error_msg) from e
```

The `get_settings` function loads the application settings from environment variables and validates them. If required environment variables are missing, it raises a `ValueError` with a helpful error message.

## Environment Variables

The following environment variables are used to configure the application:

| Variable | Description | Required |
|----------|-------------|----------|
| `PANOS_HOSTNAME` | Hostname or IP address of the Palo Alto Networks NGFW | Yes |
| `PANOS_API_KEY` | API key for authenticating with the Palo Alto Networks NGFW | Yes |
| `PANOS_DEBUG` | Enable debug logging | No (defaults to `false`) |

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
```
