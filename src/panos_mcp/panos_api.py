"""Module for interacting with PAN-OS API."""

import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

import requests
import xmltodict

from panos_mcp.config import settings


class PanOSClient:
    """Client for interacting with PAN-OS API."""

    def __init__(
        self,
        hostname: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        verify_ssl: bool = True,
    ):
        """Initialize the PAN-OS client.

        Args:
            hostname: The hostname or IP address of the PAN-OS device
            username: The username for authentication
            password: The password for authentication
            api_key: The API key for authentication
            verify_ssl: Whether to verify SSL certificates
        """
        self.hostname = hostname or settings.PANOS_HOSTNAME
        self.username = username or settings.PANOS_USERNAME
        self.password = password or settings.PANOS_PASSWORD
        self.api_key = api_key or settings.PANOS_API_KEY
        self.verify_ssl = verify_ssl if verify_ssl is not None else settings.PANOS_VERIFY_SSL
        self.base_url = f"https://{self.hostname}/api/"
        self.logger = logging.getLogger(__name__)
        self._session = requests.Session()
        self._session.verify = self.verify_ssl

    def get_api_key(self) -> str:
        """Get the API key from username and password.

        Returns:
            str: The API key
        """
        if self.api_key:
            return self.api_key

        params = {
            "type": "keygen",
            "user": self.username,
            "password": self.password,
        }

        self.logger.info("Getting API key from credentials")
        response = self._session.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()

        xml_response = response.text
        api_key = self._parse_api_key_from_xml(xml_response)

        if not api_key:
            self.logger.error("Failed to get API key from response: %s", xml_response)
            raise ValueError("Failed to get API key from response")

        self.api_key = api_key
        return api_key

    def _parse_api_key_from_xml(self, xml_response: str) -> Optional[str]:
        """Parse the API key from XML response.

        Args:
            xml_response: The XML response from the API

        Returns:
            Optional[str]: The API key or None if not found
        """
        try:
            root = ET.fromstring(xml_response)
            key_element = root.find(".//key")
            if key_element is not None and key_element.text:
                return key_element.text
        except ET.ParseError as e:
            self.logger.error("Error parsing XML response: %s", e)

        return None

    def get_security_policies(self, location: str = "vsys", vsys: str = "vsys1") -> Dict[str, Any]:
        """Get security policies from the firewall.

        Args:
            location: The location of the security policies (vsys or panorama)
            vsys: The vsys id (e.g. vsys1)

        Returns:
            Dict[str, Any]: The security policies in JSON format
        """
        self.logger.info("Getting security policies from %s location %s", location, vsys)

        # Ensure we have an API key
        if not self.api_key:
            self.get_api_key()

        # Construct the API request
        params = {
            "type": "config",
            "action": "get",
            "xpath": self._get_security_policy_xpath(location, vsys),
            "key": self.api_key,
        }

        try:
            response = self._session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            self.logger.debug("Security policies API response: %s", response.text)

            # Convert the XML response to JSON
            policies_data = xmltodict.parse(response.text)

            # Process the response
            result = self._process_security_policies_response(policies_data)
            return result
        except requests.RequestException as e:
            self.logger.error("Error fetching security policies: %s", e)
            raise

    def _get_security_policy_xpath(self, location: str, vsys: str) -> str:
        """Get the xpath for security policies based on location.

        Args:
            location: The location of the security policies (vsys or panorama)
            vsys: The vsys id (e.g. vsys1)

        Returns:
            str: The xpath for the security policies
        """
        if location.lower() == "panorama":
            return "/config/panorama/vsys/entry[@name='shared']/rulebase/security/rules"
        else:
            return f"/config/devices/entry[@name='localhost.localdomain']/vsys/entry[@name='{vsys}']/rulebase/security/rules"

    def _process_security_policies_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the security policies API response.

        Args:
            data: The parsed XML response

        Returns:
            Dict[str, Any]: Processed security policies
        """
        try:
            # Check if we got a valid response
            if "response" not in data:
                return {"error": "Invalid response format"}

            # Check if the response contains an error
            status = data["response"].get("@status", "")
            if status != "success":
                error_msg = data["response"].get("msg", {}).get("#text", "Unknown error")
                return {"error": error_msg}

            # Extract the rules
            result = data["response"].get("result", {})
            if not result:
                return {"rules": []}

            rules = result.get("rules", {})
            if not rules:
                return {"rules": []}

            entries = rules.get("entry", [])
            if not entries:
                return {"rules": []}

            # Make sure entries is always a list
            if not isinstance(entries, list):
                entries = [entries]

            # Process the rules
            processed_rules = []
            for rule in entries:
                processed_rule = self._process_single_rule(rule)
                processed_rules.append(processed_rule)

            return {"rules": processed_rules}
        except Exception as e:
            self.logger.error("Error processing security policies response: %s", e)
            return {"error": f"Error processing response: {str(e)}"}

    def _process_single_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single security rule.

        Args:
            rule: The rule data from the API response

        Returns:
            Dict[str, Any]: Processed rule data
        """
        processed_rule = {
            "name": rule.get("@name", ""),
            "description": self._get_element_text(rule, "description"),
            "enabled": not self._is_rule_disabled(rule),
            "source_zones": self._extract_list_items(rule, "from", "member"),
            "destination_zones": self._extract_list_items(rule, "to", "member"),
            "source_addresses": self._extract_list_items(rule, "source", "member"),
            "destination_addresses": self._extract_list_items(rule, "destination", "member"),
            "applications": self._extract_list_items(rule, "application", "member"),
            "services": self._extract_list_items(rule, "service", "member"),
            "categories": self._extract_list_items(rule, "category", "member"),
            "action": self._get_action(rule),
            "log_start": self._has_element(rule, "log-start"),
            "log_end": self._has_element(rule, "log-end"),
            "profile_group": self._get_element_text(rule, "profile-setting/group"),
            "tags": self._extract_list_items(rule, "tag", "member"),
        }
        return processed_rule

    def _extract_list_items(self, data: Dict[str, Any], first_key: str, second_key: str) -> List[str]:
        """Extract list items from nested dictionary.

        Args:
            data: The data dictionary
            first_key: The first level key
            second_key: The second level key containing the list items

        Returns:
            List[str]: The extracted list items
        """
        try:
            if first_key not in data:
                return []

            members = data[first_key].get(second_key, [])
            if not members:
                return []

            # If it's a string, make it a single-item list
            if isinstance(members, str):
                return [members]

            # If it's already a list, return it
            if isinstance(members, list):
                return members

            # If it's a dict with #text, extract the text
            if isinstance(members, dict) and "#text" in members:
                return [members["#text"]]

            return []
        except Exception as e:
            self.logger.error("Error extracting list items: %s", e)
            return []

    def _get_element_text(self, data: Dict[str, Any], path: str) -> str:
        """Get the text value of an element.

        Args:
            data: The data dictionary
            path: The path to the element, separated by '/'

        Returns:
            str: The text value or empty string if not found
        """
        try:
            parts = path.split("/")
            current = data

            for part in parts:
                if part not in current:
                    return ""
                current = current[part]

            # Handle different types of values
            if isinstance(current, str):
                return current
            elif isinstance(current, dict):
                return current.get("#text", "")
            else:
                return str(current)
        except Exception:
            return ""

    def _has_element(self, data: Dict[str, Any], path: str) -> bool:
        """Check if an element exists in the data.

        Args:
            data: The data dictionary
            path: The path to the element, separated by '/'

        Returns:
            bool: True if the element exists, False otherwise
        """
        try:
            parts = path.split("/")
            current = data

            for part in parts:
                if part not in current:
                    return False
                current = current[part]

            # If the element exists but is an empty dict, consider it as not existing
            if isinstance(current, dict) and not current:
                return False

            return True
        except Exception:
            return False

    def _is_rule_disabled(self, rule: Dict[str, Any]) -> bool:
        """Check if a rule is disabled.

        Args:
            rule: The rule data

        Returns:
            bool: True if the rule is disabled, False otherwise
        """
        return "disabled" in rule and rule["disabled"] == "yes"

    def _get_action(self, rule: Dict[str, Any]) -> str:
        """Get the action of a rule.

        Args:
            rule: The rule data

        Returns:
            str: The action or empty string if not found
        """
        if "action" not in rule:
            return ""

        action = rule["action"]
        if isinstance(action, str):
            return action
        elif isinstance(action, dict):
            # Sometimes the action is a complex element with just one child element
            # representing the actual action
            for key in action:
                if key != "@name" and key != "#text":  # Skip attributes
                    return key
        return ""
