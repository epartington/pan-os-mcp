#!/usr/bin/env python
"""
Simple test script to check the Palo Alto API connection directly.
This will help diagnose if there are SSL/connection issues with the firewall.
"""

import os
import ssl

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment
API_KEY = os.getenv("PANOS_API_KEY")
FIREWALL_HOST = os.getenv("PANOS_HOSTNAME")

# Print masked credentials for verification
print(f"API Key loaded: {API_KEY[:8]}...{API_KEY[-8:] if API_KEY else 'None'}")
print(f"Firewall host: {FIREWALL_HOST}")

# Create the request URL and parameters
base_url = f"https://{FIREWALL_HOST}/api/"
params = {"type": "op", "cmd": "<show><system><info></info></system></show>", "key": API_KEY}

print(f"\nAttempting to connect to {base_url}...")

# Options to try with different SSL settings
print("\n1. With SSL verification enabled (default):")
try:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(base_url, params=params)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {str(e)}")

print("\n2. With SSL verification disabled:")
try:
    with httpx.Client(timeout=10.0, verify=False) as client:
        response = client.get(base_url, params=params)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {str(e)}")

print("\n3. With custom SSL context (TLS 1.2 only):")

ssl_context = ssl.create_default_context()
ssl_context.options |= ssl.OP_NO_SSLv2
ssl_context.options |= ssl.OP_NO_SSLv3
ssl_context.options |= ssl.OP_NO_TLSv1
ssl_context.options |= ssl.OP_NO_TLSv1_1
# Only allow TLS 1.2
try:
    with httpx.Client(timeout=10.0, verify=ssl_context) as client:
        response = client.get(base_url, params=params)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {str(e)}")

# Test with explicit XML API endpoint for operational commands
print("\n4. Testing operational command endpoint:")
try:
    op_url = f"https://{FIREWALL_HOST}/api/?type=op&cmd=<show><system><info></info></system></show>&key={API_KEY}"
    masked_url = op_url.replace(API_KEY, "***API_KEY***")
    print(f"Making request to: {masked_url}")

    with httpx.Client(timeout=10.0, verify=False) as client:
        response = client.get(op_url)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {str(e)}")
