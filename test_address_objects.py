#!/usr/bin/env python3
"""Test script for PAN-OS address object retrieval."""

import logging
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_api_key(hostname: str, username: str, password: str) -> str:
    """Get API key from username and password."""
    logger.info(f"Getting API key for {username}@{hostname}")

    params = {
        "type": "keygen",
        "user": username,
        "password": password,
    }

    base_url = f"https://{hostname}/api/"
    try:
        response = requests.get(base_url, params=params, verify=False, timeout=10)
        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.text)
        key_elem = root.find(".//key")

        if key_elem is not None and key_elem.text:
            api_key = key_elem.text
            logger.info(f"Successfully obtained API key: {api_key[:5]}...")
            return api_key
        else:
            logger.error(f"Failed to find API key in response: {response.text}")
            return ""
    except Exception as e:
        logger.error(f"Error getting API key: {str(e)}")
        return ""


def get_address_objects(hostname: str, api_key: str, vsys: str = "vsys1") -> Dict[str, Any]:
    """Get address objects from PAN-OS firewall."""
    logger.info(f"Retrieving address objects from {hostname} in {vsys}")

    # Construct XPath
    xpath = f"/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='{vsys}']/address"

    # Prepare API request
    params = {
        "type": "config",
        "action": "get",
        "xpath": xpath,
        "key": api_key,
    }

    base_url = f"https://{hostname}/api/"
    try:
        response = requests.get(base_url, params=params, verify=False, timeout=30)
        response.raise_for_status()

        logger.info(f"API Response status: {response.status_code}")
        logger.debug(f"API Response content: {response.text[:500]}...")

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

                addr_obj = {"name": name, "type": "unknown"}

                # Determine address type and value
                ip_netmask = entry.find("./ip-netmask")
                if ip_netmask is not None:
                    addr_obj["type"] = "ip-netmask"
                    addr_obj["value"] = ip_netmask.text

                ip_range = entry.find("./ip-range")
                if ip_range is not None:
                    addr_obj["type"] = "ip-range"
                    addr_obj["value"] = ip_range.text

                fqdn = entry.find("./fqdn")
                if fqdn is not None:
                    addr_obj["type"] = "fqdn"
                    addr_obj["value"] = fqdn.text

                # Add description if available
                desc_elem = entry.find("./description")
                if desc_elem is not None:
                    addr_obj["description"] = desc_elem.text

                # Add tags if available
                tags_elem = entry.find("./tag")
                if tags_elem is not None:
                    tags = []
                    for tag in tags_elem.findall("./member"):
                        if tag.text:
                            tags.append(tag.text)
                    if tags:
                        addr_obj["tags"] = tags

                address_objects.append(addr_obj)
        else:
            logger.warning("No address entries found in the response")

        return {"address-objects": address_objects}

    except Exception as e:
        logger.error(f"Error retrieving address objects: {str(e)}")
        return {"error": str(e)}


def main():
    """Main entry point."""
    import argparse
    from pprint import pprint

    import urllib3

    # Disable SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    parser = argparse.ArgumentParser(description="Test PAN-OS API address object retrieval")
    parser.add_argument("--hostname", required=True, help="PAN-OS firewall hostname or IP")
    parser.add_argument("--username", required=True, help="Username for API access")
    parser.add_argument("--password", required=True, help="Password for API access")
    parser.add_argument("--vsys", default="vsys1", help="VSYS name (default: vsys1)")

    args = parser.parse_args()

    # Get API key
    api_key = get_api_key(args.hostname, args.username, args.password)
    if not api_key:
        logger.error("Failed to get API key, exiting")
        sys.exit(1)

    # Get address objects
    result = get_address_objects(args.hostname, api_key, args.vsys)

    # Display result
    if "error" in result:
        logger.error(f"Error: {result['error']}")
        sys.exit(1)

    address_objects = result.get("address-objects", [])
    logger.info(f"Found {len(address_objects)} address objects")

    if address_objects:
        print("\nAddress Objects:")
        pprint(address_objects)
    else:
        print("\nNo address objects found")


if __name__ == "__main__":
    main()
