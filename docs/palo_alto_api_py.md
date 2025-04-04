# palo_alto_api.py Documentation

This document provides a detailed explanation of the `palo_alto_api.py` module, which handles all interactions with the Palo Alto Networks firewalls through their XML API.

## File Purpose

`palo_alto_api.py` serves as the API client for communicating with Palo Alto Networks Next-Generation Firewalls (NGFWs). It:
- Manages authentication via API keys
- Constructs properly formatted API requests
- Parses XML responses
- Provides high-level functions for retrieving specific data types
- Handles error conditions and exceptions

## Import Statements

```python
import logging
import os
from typing import Dict, List, Optional

import httpx
import xmltodict
from dotenv import load_dotenv
```

### Import Details

- **Standard Library Imports**:
  - `logging`: For structured logging of API operations
  - `os`: To access environment variables containing API credentials
  - `typing`: For type hints (Dict, List, Optional)

- **External Library Imports**:
  - `httpx`: Modern async HTTP client for making API requests
  - `xmltodict`: For converting XML responses to Python dictionaries
  - `dotenv`: For loading environment variables from .env files

## Environment Setup

```python
# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger("mcp-paloalto.api")

# Environment variables for API configuration
API_KEY = os.getenv("PANOS_API_KEY")
FIREWALL_HOST = os.getenv("PANOS_HOSTNAME")
```

- Loads environment variables from a .env file if present
- Creates a logger specific to the API module
- Retrieves API credentials (API key and hostname) from environment variables

## Custom Exception Class

```python
class PaloAltoApiError(Exception):
    """Exception raised for Palo Alto API errors."""
    pass
```

- Custom exception class for API-specific errors
- Used to distinguish API errors from other exceptions in the codebase

## Core API Request Function

```python
async def make_api_request(endpoint: str, params: Optional[Dict[str, str]] = None) -> Dict:
    """
    Make an async request to the Palo Alto NGFW XML API.

    Args:
        endpoint: API endpoint to call
        params: Additional query parameters

    Returns:
        Parsed API response as a dictionary

    Raises:
        PaloAltoApiError: If the API call fails or returns an error
    """
```

- Handles the low-level details of making requests to the PAN-OS XML API
- Takes an endpoint string and optional parameters dictionary
- Returns parsed API responses as Python dictionaries
- Raises custom exceptions for all error conditions

### API Request Implementation Details

```python
if API_KEY is None or FIREWALL_HOST is None:
    raise PaloAltoApiError("API key or firewall host not configured")

# Base URL for PAN-OS XML API
base_url = f"https://{FIREWALL_HOST}/api/"

# Ensure we have query parameters with the API key
if params is None:
    params = {}
params["key"] = API_KEY
```

- Validates that required credentials are available
- Constructs the base URL for API requests
- Ensures the API key is included in all requests

### HTTP Request and Response Handling

```python
try:
    async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
        response = await client.get(base_url + endpoint, params=params)
        response.raise_for_status()

        # Debug: Log the raw XML response
        logger.debug(f"Raw XML response: {response.text[:500]}...")

        # Parse XML response to dict
        xml_dict = xmltodict.parse(response.text)

        # Debug: Log the parsed dict
        logger.debug(f"Parsed dict structure: {str(xml_dict.keys())}")
```

- Creates an async HTTP client with SSL verification disabled
- Sets a 10-second timeout for API requests
- Makes the GET request to the constructed URL with parameters
- Raises an exception for HTTP error status codes
- Logs the raw XML response (first 500 chars) for debugging
- Parses the XML response to a Python dictionary
- Logs the top-level keys of the parsed dictionary

### Response Validation and Error Handling

```python
# Check for API errors
if "response" in xml_dict and "@status" in xml_dict["response"]:
    if xml_dict["response"]["@status"] != "success":
        error_msg = "Unknown error"
        if "msg" in xml_dict["response"]:
            error_msg = xml_dict["response"]["msg"]["line"]
        raise PaloAltoApiError(f"API error: {error_msg}")

    logger.debug(f"API response keys: {str(xml_dict['response'].keys())}")
    return xml_dict["response"]
else:
    raise PaloAltoApiError("Invalid API response format")
```

- Checks if the response follows the expected format
- Validates that the response status is "success"
- Extracts error messages if the status is not successful
- Logs response details for debugging
- Returns only the "response" part of the dictionary
- Raises clear exceptions for invalid response formats

### Exception Handling

```python
except httpx.HTTPStatusError as e:
    raise PaloAltoApiError(f"HTTP error: {e.response.status_code}")
except httpx.RequestError as e:
    raise PaloAltoApiError(f"Request error: {str(e)}")
except Exception as e:
    raise PaloAltoApiError(f"Unexpected error: {str(e)}")
```

- Handles HTTP status errors (e.g., 404, 500)
- Handles request errors (connection issues, timeouts)
- Catches all other unexpected exceptions
- Wraps them in the custom PaloAltoApiError with clear messages

## Address Objects Function

```python
async def get_address_objects(location: str = "vsys", vsys: str = "vsys1") -> List[Dict]:
    """
    Retrieve address objects from the firewall.

    Args:
        location: Location type (vsys, shared, etc.)
        vsys: VSYS identifier

    Returns:
        List of address objects
    """
```

- High-level function to retrieve address objects from the firewall
- Takes location and vsys parameters with sensible defaults
- Returns a list of address objects as dictionaries

### XPath Construction and API Call

```python
params = {
    "type": "config",
    "action": "get",
    "xpath": f"/config/devices/entry[@name='localhost.localdomain']/{location}/entry[@name='{vsys}']/address",
}

try:
    response = await make_api_request("", params)
    logger.debug(f"Address objects response structure: {str(response.keys())}")
```

- Creates parameters for a configuration GET request
- Constructs the XPath to target address objects in the specified location
- Makes the API request using the core function
- Logs the structure of the response

### Processing Address Objects

```python
addresses = []
if "result" in response:
    # Debug the result structure
    logger.debug(f"Result structure: {str(response['result'])[:500]}...")

    address_entries = response["result"].get("address", {}).get("entry", [])
    logger.debug(f"Address entries type: {type(address_entries)}")

    # Handle single entry response (not in a list)
    if isinstance(address_entries, dict):
        logger.debug(f"Single address entry: {str(address_entries)}")
        address_entries = [address_entries]
    elif isinstance(address_entries, list):
        logger.debug(f"Multiple address entries: {len(address_entries)}")
    else:
        logger.debug(f"Unexpected address entries type: {type(address_entries)}")
```

- Initializes an empty list for processed address objects
- Extracts the result portion of the response
- Gets the address entries from the result
- Handles both single entries (dict) and multiple entries (list)
- Normalizes the data structure to always work with a list

### Processing Individual Addresses

```python
for entry in address_entries:
    address = {"name": entry["@name"], "type": None, "value": None}

    # Determine address type and value
    if "ip-netmask" in entry:
        address["type"] = "ip-netmask"
        address["value"] = entry["ip-netmask"]
    elif "ip-range" in entry:
        address["type"] = "ip-range"
        address["value"] = entry["ip-range"]
    elif "fqdn" in entry:
        address["type"] = "fqdn"
        address["value"] = entry["fqdn"]

    addresses.append(address)
    logger.debug(f"Processed address: {address}")
```

- Extracts the name of each address object
- Determines the address type (ip-netmask, ip-range, or fqdn)
- Extracts the corresponding value
- Creates a standardized address object dictionary
- Adds it to the addresses list
- Logs each processed address for debugging

### Finalizing and Error Handling

```python
logger.debug(f"Final addresses list: {addresses}")
return addresses

except PaloAltoApiError as e:
    logger.error(f"Error retrieving address objects: {str(e)}")
    raise
```

- Logs the final list of processed address objects
- Returns the list to the caller
- Catches and logs API errors
- Re-raises the exception to be handled by the caller

## Security Zones Function

```python
async def get_security_zones(location: str = "vsys", vsys: str = "vsys1") -> List[Dict]:
    """
    Retrieve security zones from the firewall.

    Args:
        location: Location type (vsys, shared, etc.)
        vsys: VSYS identifier

    Returns:
        List of security zones
    """
```

- Similar structure to the get_address_objects function
- Retrieves security zones instead of address objects
- Takes the same location and vsys parameters
- Returns a list of security zone dictionaries

## Security Policies Function

```python
async def get_security_policies(location: str = "vsys", vsys: str = "vsys1") -> List[Dict]:
    """
    Retrieve security policies from the firewall.

    Args:
        location: Location type (vsys, shared, etc.)
        vsys: VSYS identifier

    Returns:
        List of security policies
    """
```

- Similar structure to the other getter functions
- Retrieves security policies from the firewall
- Returns them as a list of standardized dictionaries
