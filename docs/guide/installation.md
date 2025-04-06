# Installation

This guide covers how to install the Palo Alto Networks MCP Server.

## Prerequisites

- Python 3.10 or later
- Palo Alto Networks NGFW with XML API access
- API key with appropriate permissions

## Installation Steps

### Using pip

```bash
pip install .
```

### Using uv (recommended)

```bash
uv pip install .
```

## Development Installation

For development purposes, you can install the package in editable mode:

```bash
# Using pip
pip install -e .

# Using uv
uv pip install -e .
```

## Virtual Environment

It's recommended to use a virtual environment for installation:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install the package
pip install .
```

## Dependencies

The main dependencies include:

- `modelcontextprotocol`: The MCP Python SDK
- `httpx`: For making asynchronous HTTP requests
- `pydantic-settings`: For configuration management
