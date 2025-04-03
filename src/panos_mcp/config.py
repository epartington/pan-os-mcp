"""Configuration settings for the PAN-OS MCP Server."""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API settings
    api_prefix: str = "/mcp"

    # PAN-OS settings
    panos_api_key: str = os.getenv("PANOS_API_KEY", "")
    panos_hostname: str = os.getenv("PANOS_HOSTNAME", "")
    panos_username: str = os.getenv("PANOS_USERNAME", "")
    panos_password: str = os.getenv("PANOS_PASSWORD", "")
    panos_verify_ssl: bool = os.getenv("PANOS_VERIFY_SSL", "False").lower() == "true"

    # Logging settings
    log_level: str = os.getenv("LOG_LEVEL", "info")

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
