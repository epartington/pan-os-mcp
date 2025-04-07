#!/usr/bin/env python3
"""
Generate Palo Alto Networks API Key

This script generates an API key for Palo Alto Networks devices using the
credentials from environment variables PANOS_USER and PANOS_PASS.
"""

import asyncio
import os
import sys
import xml.etree.ElementTree as ET

import httpx

# Suppress insecure request warnings


async def generate_api_key() -> str | None:
    """Generate an API key using environment variables."""
    # Get credentials from environment
    hostname = os.environ.get("PANOS_HOST", "")
    username = os.environ.get("PANOS_USER", "")
    password = os.environ.get("PANOS_PASS", "")

    if not hostname or not username or not password:
        print("Error: Required environment variables not set.")
        print("Please ensure PANOS_HOST, PANOS_USER, and PANOS_PASS are set.")
        sys.exit(1)

    print(f"Generating API key for {username}@{hostname}...")

    # Construct the API URL
    url = f"https://{hostname}/api/"
    params = {"type": "keygen", "user": username, "password": password}

    try:
        # Make the API request
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, params=params, timeout=30.0)

            if response.status_code == 200:
                # Parse the XML response
                root = ET.fromstring(response.text)
                status = root.get("status")

                if status == "success":
                    # Extract the API key
                    key_element = root.find(".//key")
                    if key_element is not None and key_element.text:
                        api_key = key_element.text
                        print("\nAPI Key generated successfully!")
                        print("\nAPI Key:")
                        print(f"{api_key}")

                        # Print instructions for using the API key
                        print("\nTo use this API key:")
                        print(f'export PANOS_API_KEY="{api_key}"')
                        print("\nOr add it to your .zshrc file:")
                        print(f'export PANOS_API_KEY="{api_key}"')
                        print("\nOr update your mcp_config.json:")
                        print(f'"PANOS_API_KEY": "{api_key}"')
                        return api_key
                    else:
                        print("Error: Could not find API key in response")
                else:
                    # Extract error message
                    error = root.find(".//msg")
                    if error is not None and error.text:
                        print(f"Error: {error.text}")
                    else:
                        print("Unknown error occurred")
            else:
                print(f"HTTP Error: {response.status_code}")
                print(response.text)

    except httpx.RequestError as e:
        print(f"Connection error: {str(e)}")
    except ET.ParseError as e:
        print(f"XML parsing error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

    return None


async def main() -> None:
    """Main entry point for the script."""
    await generate_api_key()


if __name__ == "__main__":
    asyncio.run(main())
