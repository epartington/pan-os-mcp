"""
Palo Alto Networks API Integration Module

This module handles interactions with the Palo Alto Networks Next-Generation
Firewall (NGFW) XML API using asynchronous HTTP requests.
"""

import logging
import os
from typing import Dict, List, Optional

import httpx
import xmltodict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger("mcp-paloalto.api")

# Environment variables for API configuration
API_KEY = os.getenv("PANOS_API_KEY")
FIREWALL_HOST = os.getenv("PANOS_HOSTNAME")

# Debug logging for environment variables
if API_KEY:
    masked_key = API_KEY[:8] + "..." + API_KEY[-8:] if len(API_KEY) > 16 else "***masked***"
    logger.debug(f"Loaded API_KEY from environment: {masked_key}")
else:
    logger.error("Failed to load PANOS_API_KEY from environment")

if FIREWALL_HOST:
    logger.debug(f"Loaded FIREWALL_HOST from environment: {FIREWALL_HOST}")
else:
    logger.error("Failed to load PANOS_HOSTNAME from environment")


class PaloAltoApiError(Exception):
    """Exception raised for Palo Alto API errors."""

    pass


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
    if API_KEY is None or FIREWALL_HOST is None:
        logger.error("API key or firewall host not configured")
        raise PaloAltoApiError("API key or firewall host not configured")

    # Base URL for PAN-OS XML API
    base_url = f"https://{FIREWALL_HOST}/api/"
    logger.debug(f"Making API request to: {base_url + endpoint}")

    # Ensure we have query parameters with the API key
    if params is None:
        params = {}
    params["key"] = API_KEY

    # Log parameters (with masked API key)
    debug_params = params.copy()
    if "key" in debug_params:
        debug_params["key"] = "***masked***"
    logger.debug(f"Request parameters: {debug_params}")

    try:
        logger.debug("Creating AsyncClient with SSL verification disabled and 10s timeout")
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            logger.debug(f"Sending GET request to {base_url + endpoint}")
            response = await client.get(base_url + endpoint, params=params)
            logger.debug(f"Received response with status code: {response.status_code}")
            response.raise_for_status()

            # Debug: Log the raw XML response
            logger.debug(f"Raw XML response: {response.text[:500]}...")

            # Parse XML response to dict
            logger.debug("Parsing XML response to dictionary")
            xml_dict = xmltodict.parse(response.text)

            # Debug: Log the parsed dict
            logger.debug(f"Parsed dict structure: {str(xml_dict.keys())}")

            # Check for API errors
            if "response" in xml_dict and "@status" in xml_dict["response"]:
                if xml_dict["response"]["@status"] != "success":
                    error_msg = "Unknown error"
                    if "msg" in xml_dict["response"]:
                        error_msg = xml_dict["response"]["msg"]["line"]
                    logger.error(f"API returned error: {error_msg}")
                    raise PaloAltoApiError(f"API error: {error_msg}")

                logger.debug(f"API response keys: {str(xml_dict['response'].keys())}")
                return xml_dict["response"]
            else:
                logger.error("Invalid API response format")
                raise PaloAltoApiError("Invalid API response format")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code}")
        logger.error(f"Response content: {e.response.text[:500]}")
        raise PaloAltoApiError(f"HTTP error: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Request error: {str(e)}")
        raise PaloAltoApiError(f"Request error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise PaloAltoApiError(f"Unexpected error: {str(e)}")


async def get_address_objects(location: str = "vsys", vsys: str = "vsys1") -> List[Dict]:
    """
    Retrieve address objects from the firewall.

    Args:
        location: Location type (vsys, shared, etc.)
        vsys: VSYS identifier

    Returns:
        List of address objects
    """
    params = {
        "type": "config",
        "action": "get",
        "xpath": f"/config/devices/entry[@name='localhost.localdomain']/{location}/entry[@name='{vsys}']/address",
    }

    try:
        response = await make_api_request("", params)
        logger.debug(f"Address objects response structure: {str(response.keys())}")

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

        logger.debug(f"Final addresses list: {addresses}")
        return addresses

    except PaloAltoApiError as e:
        logger.error(f"Error retrieving address objects: {str(e)}")
        raise


async def get_security_zones(location: str = "vsys", vsys: str = "vsys1") -> List[Dict]:
    """
    Retrieve security zones from the firewall.

    Args:
        location: Location type (vsys, shared, etc.)
        vsys: VSYS identifier

    Returns:
        List of security zones
    """
    params = {
        "type": "config",
        "action": "get",
        "xpath": f"/config/devices/entry[@name='localhost.localdomain']/{location}/entry[@name='{vsys}']/zone",
    }

    try:
        response = await make_api_request("", params)

        zones = []
        if "result" in response:
            zone_entries = response["result"].get("zone", {}).get("entry", [])

            # Handle single entry response (not in a list)
            if isinstance(zone_entries, dict):
                zone_entries = [zone_entries]

            for entry in zone_entries:
                zone = {"name": entry["@name"], "mode": None, "interfaces": []}

                # Determine zone mode and interfaces
                if "network" in entry:
                    network = entry["network"]

                    if "layer3" in network:
                        zone["mode"] = "layer3"
                        interfaces = network["layer3"].get("member", [])
                        if isinstance(interfaces, str):
                            interfaces = [interfaces]
                        zone["interfaces"] = interfaces
                    elif "layer2" in network:
                        zone["mode"] = "layer2"
                        interfaces = network["layer2"].get("member", [])
                        if isinstance(interfaces, str):
                            interfaces = [interfaces]
                        zone["interfaces"] = interfaces
                    elif "virtual-wire" in network:
                        zone["mode"] = "virtual-wire"
                        interfaces = network["virtual-wire"].get("member", [])
                        if isinstance(interfaces, str):
                            interfaces = [interfaces]
                        zone["interfaces"] = interfaces
                    elif "tap" in network:
                        zone["mode"] = "tap"
                        interfaces = network["tap"].get("member", [])
                        if isinstance(interfaces, str):
                            interfaces = [interfaces]
                        zone["interfaces"] = interfaces

                zones.append(zone)

        return zones

    except PaloAltoApiError as e:
        logger.error(f"Error retrieving security zones: {str(e)}")
        raise


async def get_security_policies(location: str = "vsys", vsys: str = "vsys1") -> List[Dict]:
    """
    Retrieve security policies from the firewall.

    Args:
        location: Location type (vsys, shared, etc.)
        vsys: VSYS identifier

    Returns:
        List of security policies
    """
    params = {
        "type": "config",
        "action": "get",
        "xpath": (
            f"/config/devices/entry[@name='localhost.localdomain']/{location}/entry[@name='{vsys}']/rulebase/security/rules"
        ),
    }

    try:
        response = await make_api_request("", params)

        policies = []
        if "result" in response:
            policy_entries = response["result"].get("rules", {}).get("entry", [])

            # Handle single entry response (not in a list)
            if isinstance(policy_entries, dict):
                policy_entries = [policy_entries]

            for entry in policy_entries:
                policy = {
                    "name": entry["@name"],
                    "enabled": entry.get("disabled") != "yes",
                    "source_zones": _get_list_from_member(entry.get("from", {}).get("member", [])),
                    "destination_zones": _get_list_from_member(entry.get("to", {}).get("member", [])),
                    "source_addresses": _get_list_from_member(entry.get("source", {}).get("member", [])),
                    "destination_addresses": _get_list_from_member(entry.get("destination", {}).get("member", [])),
                    "applications": _get_list_from_member(entry.get("application", {}).get("member", [])),
                    "services": _get_list_from_member(entry.get("service", {}).get("member", [])),
                    "action": entry.get("action", ""),
                }

                policies.append(policy)

        return policies

    except PaloAltoApiError as e:
        logger.error(f"Error retrieving security policies: {str(e)}")
        raise


def _get_list_from_member(member_entry):
    """Helper function to convert member entries to lists."""
    if not member_entry:
        return []
    if isinstance(member_entry, str):
        return [member_entry]
    return member_entry
