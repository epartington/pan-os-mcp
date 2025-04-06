# Contributing

Thank you for considering contributing to the Palo Alto Networks MCP Server! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## Reporting Bugs

If you find a bug, please create an issue on the GitHub repository with the following information:

- A clear and descriptive title
- A detailed description of the bug
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Any relevant logs or error messages
- Your environment (Python version, operating system, etc.)

## Suggesting Enhancements

If you have an idea for an enhancement, please create an issue on the GitHub repository with the following information:

- A clear and descriptive title
- A detailed description of the enhancement
- Any relevant examples or use cases
- Any potential implementation details

## Code Contribution Workflow

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Write tests for your changes
5. Run the tests to ensure they pass
6. Submit a pull request

### Fork the Repository

Click the "Fork" button at the top right of the GitHub repository page to create a copy of the repository in your GitHub account.

### Create a Branch

Create a new branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

### Make Your Changes

Make your changes to the codebase. Be sure to follow the code style guidelines and write tests for your changes.

### Write Tests

Write tests for your changes to ensure they work as expected and to prevent regressions in the future.

### Run Tests

Run the tests to ensure they pass:

```bash
pytest
```

### Submit a Pull Request

Push your changes to your fork and submit a pull request to the main repository.

## Code Style Guidelines

This project follows the [Black](https://black.readthedocs.io/) code style. Please ensure your code is formatted according to these guidelines.

You can use the following tools to check and format your code:

- [Black](https://black.readthedocs.io/) for code formatting
- [Flake8](https://flake8.pycqa.org/) for linting
- [isort](https://pycqa.github.io/isort/) for import sorting

```bash
# Format code
black .

# Check code style
flake8

# Sort imports
isort .
```

## Setting Up Development Environment

1. Clone the repository:

```bash
git clone https://github.com/cdot65/pan-os-mcp.git
cd pan-os-mcp
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:

```bash
pip install -e ".[dev]"
```

4. Create a `.env` file with your development environment variables:

```
PANOS_HOSTNAME=your-firewall-hostname
PANOS_API_KEY=your-api-key
PANOS_DEBUG=true
```

## Documentation

When making changes, please update the documentation as needed. This project uses [MkDocs](https://www.mkdocs.org/) with the [Material](https://squidfunk.github.io/mkdocs-material/) theme for documentation.

To build and view the documentation locally:

```bash
# Install mkdocs and the material theme
pip install mkdocs mkdocs-material

# Build and serve the documentation
mkdocs serve
```

Then open http://127.0.0.1:8000 in your browser.

## Release Process

1. Update the version number in `pyproject.toml`
2. Update the CHANGELOG.md file
3. Create a new release on GitHub
4. Tag the release with the version number
5. Publish the package to PyPI (if applicable)

Thank you for your contributions!
