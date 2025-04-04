#!/usr/bin/env python3
"""Test script for PAN-OS address object retrieval."""

import logging
import os
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_address_objects(hostname: str, api_key: str, location: str = "vsys", vsys: str = "vsys1") -> Dict[str, Any]:
    """Get address objects from PAN-OS firewall."""
    logger.info(f"Retrieving address objects from {hostname} in {location}/{vsys}")

    # Construct XPath
    xpath = f"/config/devices/entry[@name='localhost.localdomain']/{location}/entry[@name='{vsys}']/address"
    logger.debug(f"Using XPath: {xpath}")

    # Prepare API request
    params = {
        "type": "config",
        "action": "get",
        "xpath": xpath,
        "key": api_key,
    }

    base_url = f"https://{hostname}/api/"
    try:
        logger.debug(f"Making API request to {base_url} with params (key masked)")
        debug_params = params.copy()
        debug_params["key"] = "***MASKED***"
        logger.debug(f"Parameters: {debug_params}")

        response = requests.get(base_url, params=params, verify=False, timeout=30)
        logger.debug(f"API Response status: {response.status_code}")
        logger.debug(f"API Response headers: {response.headers}")
        logger.debug(f"API Response content: {response.text[:500]}...")

        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.text)
        status = root.get("status")

        if status != "success":
            error_msg = root.find("./msg")
            error_text = error_msg.text if error_msg is not None else "Unknown error"
            logger.error(f"API error: {error_text}")
            return {"error": error_text}

        # Process address objects
        address_objects = []
        result_elem = root.find("./result/address")

        if result_elem is not None:
            logger.info(f"Found {len(list(result_elem))} address entries")

            for entry in result_elem.findall("./entry"):
                name = entry.get("name", "")
                logger.info(f"Processing address entry: {name}")

                addr_obj = {"name": name, "type": "unknown", "value": None}

                # Determine address type and value
                ip_netmask = entry.find("./ip-netmask")
                if ip_netmask is not None and ip_netmask.text:
                    addr_obj["type"] = "ip-netmask"
                    addr_obj["value"] = ip_netmask.text

                ip_range = entry.find("./ip-range")
                if ip_range is not None and ip_range.text:
                    addr_obj["type"] = "ip-range"
                    addr_obj["value"] = ip_range.text

                fqdn = entry.find("./fqdn")
                if fqdn is not None and fqdn.text:
                    addr_obj["type"] = "fqdn"
                    addr_obj["value"] = fqdn.text

                address_objects.append(addr_obj)

            return {"address_objects": address_objects}
        else:
            logger.warning("No address entries found in the response")
            return {"address_objects": []}

    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error: {str(e)}")
        return {"error": f"HTTP error: {str(e)}"}
    except ET.ParseError as e:
        logger.error(f"XML parsing error: {str(e)}")
        return {"error": f"XML parsing error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


def main():
    """Main entry point."""
    # Get API key and hostname from .env file
    api_key = os.getenv("PANOS_API_KEY")
    hostname = os.getenv("PANOS_HOSTNAME")

    if not api_key or not hostname:
        logger.error("API key or hostname not found in environment variables")
        sys.exit(1)

    # Mask API key for logging
    masked_key = f"{api_key[:8]}...{api_key[-8:]}" if len(api_key) > 16 else "***MASKED***"
    logger.info(f"Using API key: {masked_key}")
    logger.info(f"Using hostname: {hostname}")

    # Get address objects
    result = get_address_objects(hostname, api_key)

    if "error" in result:
        logger.error(f"Failed to retrieve address objects: {result['error']}")
        sys.exit(1)

    # Print address objects
    address_objects = result.get("address_objects", [])
    logger.info(f"Retrieved {len(address_objects)} address objects")

    print("\nAddress Objects:")
    print("===============")
    for obj in address_objects:
        print(f"Name: {obj['name']}")
        print(f"Type: {obj['type']}")
        print(f"Value: {obj['value']}")
        print("---------------")


if __name__ == "__main__":
    main()
