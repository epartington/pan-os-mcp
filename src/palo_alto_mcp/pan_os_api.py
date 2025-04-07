"""Palo Alto Networks XML API client module."""

import logging
import xml.etree.ElementTree as ElementTree
from typing import TypeVar

import httpx

from palo_alto_mcp.config import Settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PanOSAPIClient:
    """Client for interacting with the Palo Alto Networks XML API.

    This class provides methods for retrieving data from a Palo Alto Networks
    Next-Generation Firewall (NGFW) through its XML API.

    Attributes:
        hostname: The hostname or IP address of the NGFW.
        api_key: The API key for authenticating with the NGFW.
        client: An httpx AsyncClient for making HTTP requests.

    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the PanOSAPIClient.

        Args:
            settings: Application settings containing NGFW connection information.

        """
        self.hostname = settings.panos_hostname
        self.api_key = settings.panos_api_key
        self.base_url = f"https://{self.hostname}/api/"
        self.client = httpx.AsyncClient(verify=False)  # In production, use proper cert verification

    async def __aenter__(self) -> "PanOSAPIClient":
        """Async context manager entry.

        Returns:
            The PanOSAPIClient instance.

        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Async context manager exit.

        Args:
            exc_type: The exception type, if any.
            exc_val: The exception value, if any.
            exc_tb: The exception traceback, if any.

        """
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def _make_request(self, params: dict[str, str]) -> ElementTree.Element:
        """Make a request to the Palo Alto Networks XML API.

        Args:
            params: Dictionary of query parameters to include in the request.

        Returns:
            The XML response as an ElementTree Element.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
            ValueError: If the API returns an error response.

        """
        # Add the API key to the parameters
        params["key"] = self.api_key

        try:
            logger.debug(f"Making API request to {self.base_url} with params: {params}")
            response = await self.client.get(self.base_url, params=params, timeout=30.0)
            response.raise_for_status()

            # Parse the XML response
            response_text = response.text
            if not response_text:
                raise ValueError("Empty response from API")

            logger.debug(f"Received response: {response_text[:200]}..." if len(response_text) > 200 else response_text)

            root = ElementTree.fromstring(response_text)

            # Check for API errors
            status = root.get("status")
            if status != "success":
                error_msg = "Unknown error"
                error_element = root.find(".//msg")
                if error_element is not None and error_element.text is not None:
                    error_msg = error_element.text
                raise ValueError(f"API error: {error_msg}") from None

            return root
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {str(e)}")
            raise httpx.HTTPError(f"HTTP error: {str(e)}") from e
        except ElementTree.ParseError as e:
            logger.error(f"XML parsing error: {str(e)}")
            raise ValueError(f"Failed to parse XML response: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception(f"Unexpected error: {str(e)}") from e

    async def get_system_info(self) -> dict[str, str]:
        """Get system information from the firewall.

        Returns:
            Dictionary containing system information.

        """
        # Use the correct XML command format that works with this firewall
        params = {"type": "op", "cmd": "<show><system><info></info></system></show>"}

        root = await self._make_request(params)
        result = root.find(".//result")

        if result is None:
            raise ValueError("No system information found in response")

        # Extract system information
        system_info = {}

        # Handle the case where result has a 'system' child element
        system_elem = result.find("system")
        if system_elem is not None:
            for child in system_elem:
                if child.text is not None:
                    system_info[child.tag] = child.text
                else:
                    system_info[child.tag] = ""
        else:
            # Handle the case where result contains the system info directly
            for child in result:
                if child.text is not None:
                    system_info[child.tag] = child.text
                else:
                    system_info[child.tag] = ""

        # If no system info was found, add a default message
        if not system_info:
            system_info["status"] = "Connected to firewall, but no detailed system information available"

        return system_info

    async def get_address_objects(self) -> list[dict[str, str]]:
        """Get address objects configured on the firewall.

        Returns:
            List of dictionaries containing address object information.
            Each dictionary contains name, type, value, and optionally description and location.

        """
        address_objects = []
        logger.info("Retrieving address objects from Panorama")

        # 1. Get shared address objects
        shared_params = {"type": "config", "action": "get", "xpath": "/config/shared/address"}
        try:
            logger.info("Retrieving shared address objects")
            root = await self._make_request(shared_params)

            # Log the structure of the response for debugging
            logger.debug(f"Shared address response structure: {ElementTree.tostring(root, encoding='unicode')[:200]}...")

            shared_entries = root.findall(".//entry")
            logger.info(f"Found {len(shared_entries)} shared address objects")

            for entry in shared_entries:
                address_obj = {"name": entry.get("name") or "", "location": "shared"}

                # Process the address object
                address_objects.append(self._process_address_entry(entry, address_obj))

        except Exception as e:
            logger.error(f"Error retrieving shared address objects: {str(e)}")

        # 2. Get device group address objects
        try:
            # First, get the list of device groups
            logger.info("Retrieving device groups")
            dg_list_params = {"type": "config", "action": "get", "xpath": "/config/devices/entry/device-group"}
            dg_root = await self._make_request(dg_list_params)

            # Log the structure of the response for debugging
            logger.debug(f"Device group response structure: {ElementTree.tostring(dg_root, encoding='unicode')[:200]}...")

            device_groups = dg_root.findall(".//entry")
            logger.info(f"Found {len(device_groups)} device groups")

            for dg in device_groups:
                dg_name = dg.get("name")
                if not dg_name:
                    continue

                logger.info(f"Retrieving address objects for device group '{dg_name}'")
                # Get addresses for this device group
                dg_addr_params = {
                    "type": "config",
                    "action": "get",
                    "xpath": f"/config/devices/entry/device-group/entry[@name='{dg_name}']/address",
                }

                try:
                    dg_addr_root = await self._make_request(dg_addr_params)

                    # Log the structure of the response for debugging
                    logger.debug(
                        f"Device group '{dg_name}' address response: {ElementTree.tostring(dg_addr_root, encoding='unicode')[:200]}..."
                    )

                    dg_entries = dg_addr_root.findall(".//entry")
                    logger.info(f"Found {len(dg_entries)} address objects in device group '{dg_name}'")

                    for entry in dg_entries:
                        address_obj = {"name": entry.get("name") or "", "location": f"device-group:{dg_name}"}

                        # Process the address object
                        address_objects.append(self._process_address_entry(entry, address_obj))

                except Exception as e:
                    logger.error(f"Error retrieving address objects for device group '{dg_name}': {str(e)}")

        except Exception as e:
            logger.error(f"Error retrieving device groups: {str(e)}")

        # 3. Get vsys address objects (for backward compatibility with firewalls)
        logger.info("Retrieving vsys address objects (for backward compatibility)")
        vsys_params = {"type": "config", "action": "get", "xpath": "/config/devices/entry/vsys/entry/address"}
        try:
            root = await self._make_request(vsys_params)
            vsys_entries = root.findall(".//entry")
            logger.info(f"Found {len(vsys_entries)} vsys address objects")

            # Find vsys name from the xpath rather than parent reference
            # since standard ElementTree doesn't have getparent()
            for entry in vsys_entries:
                # Default to "unknown" if we can't determine the vsys name
                vsys_name = "unknown"
                address_obj = {"name": entry.get("name") or "", "location": f"vsys:{vsys_name}"}

                # Process the address object
                address_objects.append(self._process_address_entry(entry, address_obj))

        except Exception as e:
            # This might fail on Panorama, which is expected
            logger.debug(f"Note: vsys address objects retrieval: {str(e)}")

        logger.info(f"Total address objects found: {len(address_objects)}")
        return address_objects

    def _process_address_entry(self, entry: ElementTree.Element, address_obj: dict[str, str]) -> dict[str, str]:
        """Process an address entry XML element and extract its properties.

        Args:
            entry: The XML element representing an address object
            address_obj: Partially populated address object dictionary

        Returns:
            Fully populated address object dictionary
        """
        # Check for different address types
        ip_netmask = entry.find("ip-netmask")
        if ip_netmask is not None and ip_netmask.text is not None:
            address_obj["type"] = "ip-netmask"
            address_obj["value"] = ip_netmask.text
        elif (ip_range := entry.find("ip-range")) is not None and ip_range.text is not None:
            address_obj["type"] = "ip-range"
            address_obj["value"] = ip_range.text
        elif (fqdn := entry.find("fqdn")) is not None and fqdn.text is not None:
            address_obj["type"] = "fqdn"
            address_obj["value"] = fqdn.text
        else:
            address_obj["type"] = "unknown"
            address_obj["value"] = ""

        # Get description if available
        description = entry.find("description")
        if description is not None and description.text is not None:
            address_obj["description"] = description.text

        # Get tags if available
        tags = []
        tag_elements = entry.findall("tag/member")
        if tag_elements:
            for tag in tag_elements:
                if tag.text:
                    tags.append(tag.text)
            if tags:
                address_obj["tags"] = ", ".join(tags)

        return address_obj

    async def get_security_zones(self) -> list[dict[str, str]]:
        """Get security zones configured on the firewall.

        Returns:
            List of dictionaries containing security zone information.

        """
        params = {"type": "config", "action": "get", "xpath": "/config/devices/entry/vsys/entry/zone"}

        root = await self._make_request(params)
        entries = root.findall(".//entry")

        zones = []
        for entry in entries:
            zone = {"name": entry.get("name") or ""}

            # Get zone type
            if entry.find("network/layer3") is not None:
                zone["type"] = "layer3"
                interfaces = entry.findall(".//member")
                zone["interfaces"] = ",".join([interface.text for interface in interfaces if interface.text])
            elif entry.find("network/layer2") is not None:
                zone["type"] = "layer2"
                interfaces = entry.findall(".//member")
                zone["interfaces"] = ",".join([interface.text for interface in interfaces if interface.text])
            elif entry.find("network/virtual-wire") is not None:
                zone["type"] = "virtual-wire"
                interfaces = entry.findall(".//member")
                zone["interfaces"] = ",".join([interface.text for interface in interfaces if interface.text])
            elif entry.find("network/tap") is not None:
                zone["type"] = "tap"
                interfaces = entry.findall(".//member")
                zone["interfaces"] = ",".join([interface.text for interface in interfaces if interface.text])
            elif entry.find("network/external") is not None:
                zone["type"] = "external"
                zone["interfaces"] = ""
            else:
                zone["type"] = "unknown"
                zone["interfaces"] = ""

            zones.append(zone)

        return zones

    async def get_security_policies(self) -> list[dict[str, str]]:
        """Get security policies configured on the firewall.

        Returns:
            List of dictionaries containing security policy information.

        """
        params = {"type": "config", "action": "get", "xpath": "/config/devices/entry/vsys/entry/rulebase/security/rules"}

        root = await self._make_request(params)
        entries = root.findall(".//entry")

        policies = []
        for entry in entries:
            policy = {"name": entry.get("name") or ""}

            # Source information
            source_zones = entry.findall(".//from/member")
            policy["source_zones"] = ",".join([zone.text for zone in source_zones if zone.text])

            source_addresses = entry.findall(".//source/member")
            policy["source_addresses"] = ",".join([addr.text for addr in source_addresses if addr.text])

            # Destination information
            dest_zones = entry.findall(".//to/member")
            policy["destination_zones"] = ",".join([zone.text for zone in dest_zones if zone.text])

            dest_addresses = entry.findall(".//destination/member")
            policy["destination_addresses"] = ",".join([addr.text for addr in dest_addresses if addr.text])

            # Application and service information
            applications = entry.findall(".//application/member")
            policy["applications"] = ",".join([app.text for app in applications if app.text])

            services = entry.findall(".//service/member")
            policy["services"] = ",".join([svc.text for svc in services if svc.text])

            # Action
            action = entry.find("action")
            if action is not None and action.text is not None:
                policy["action"] = action.text
            else:
                policy["action"] = ""

            # Description
            description = entry.find("description")
            if description is not None and description.text is not None:
                policy["description"] = description.text
            else:
                policy["description"] = ""

            policies.append(policy)

        return policies
