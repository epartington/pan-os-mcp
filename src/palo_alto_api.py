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
        raise PaloAltoApiError("API key or firewall host not configured")

    # Base URL for PAN-OS XML API
    base_url = f"https://{FIREWALL_HOST}/api/"

    # Ensure we have query parameters with the API key
    if params is None:
        params = {}
    params["key"] = API_KEY

    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(base_url + endpoint, params=params)
            response.raise_for_status()

            # Parse XML response to dict
            xml_dict = xmltodict.parse(response.text)

            # Check for API errors
            if "response" in xml_dict and "@status" in xml_dict["response"]:
                if xml_dict["response"]["@status"] != "success":
                    error_msg = "Unknown error"
                    if "msg" in xml_dict["response"]:
                        error_msg = xml_dict["response"]["msg"]["line"]
                    raise PaloAltoApiError(f"API error: {error_msg}")

                return xml_dict["response"]
            else:
                raise PaloAltoApiError("Invalid API response format")

    except httpx.HTTPStatusError as e:
        raise PaloAltoApiError(f"HTTP error: {e.response.status_code}")
    except httpx.RequestError as e:
        raise PaloAltoApiError(f"Request error: {str(e)}")
    except Exception as e:
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

        addresses = []
        if "result" in response:
            address_entries = response["result"].get("address", {}).get("entry", [])

            # Handle single entry response (not in a list)
            if isinstance(address_entries, dict):
                address_entries = [address_entries]

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
