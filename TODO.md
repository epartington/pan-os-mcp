# TODO List: MCP Palo Alto Integration Server (Python SDK)

## Phase 1: Project Setup & API Client

- [ ] **Initialize Project Environment:**
  - [ ] Create the main project directory (`palo-alto-mcp`).
  - [ ] Initialize the project using `uv init`.
  - [ ] Set up the basic directory structure:
    - `src/palo_alto_mcp/`
    - `tests/`
- [ ] **Configure `pyproject.toml`:**
  - [ ] Define project metadata (name, version source, authors, etc.).
  - [ ] Add core dependencies: `mcp`, `httpx`.
  - [ ] Add optional dependencies if using: `pydantic-settings`.
  - [ ] Add development dependencies: `pytest`, `ruff`, `pyright`/`mypy`.
  - [ ] Configure build system (`hatchling`, `uv-dynamic-versioning`).
  - [ ] Configure linters/formatters (`ruff`, `pyright`).
- [ ] **Create Basic Python Files:**
  - [ ] `src/palo_alto_mcp/__init__.py` (can be empty).
  - [ ] `src/palo_alto_mcp/pan_os_api.py` (for API client logic).
  - [ ] `src/palo_alto_mcp/server.py` (for `FastMCP` implementation).
  - [ ] `src/palo_alto_mcp/__main__.py` (for entry point).
- [ ] **Implement Configuration Loading:**
  - [ ] Define required environment variables (`PANOS_HOSTNAME`, `PANOS_API_KEY`).
  - [ ] (Optional) Implement loading using `pydantic-settings` in `server.py` or a dedicated `config.py`.
- [ ] **Implement Palo Alto API Client (`pan_os_api.py`):**
  - [ ] Implement connection logic using `httpx` (HTTPS, base URL from config).
  - [ ] Implement authentication logic using API key (from config).
  - [ ] Implement function to fetch Address Objects (send request, handle XML response).
  - [ ] Implement function to fetch Security Zones (send request, handle XML response).
  - [ ] Implement function to fetch Security Policies (send request, handle XML response).
  - [ ] Implement basic error handling for API requests (e.g., connection errors, auth failures, non-200 responses).

## Phase 2: `FastMCP` Server Implementation

- [ ] **Instantiate `FastMCP` (`server.py`):**
  - [ ] Import `FastMCP` from `mcp.server.fastmcp`.
  - [ ] Create an instance: `mcp = FastMCP("PaloAltoMCPServer", ...)`.
  - [ ] Load configuration (hostname, API key) needed by tools.
- [ ] **Implement `retrieve_address_objects` Tool (`server.py`):**
  - [ ] Define a Python function (e.g., `get_address_objects`).
  - [ ] Add the `@mcp.tool()` decorator.
  - [ ] Add type hints for any arguments (if required) and the return value.
  - [ ] Call the corresponding function from `pan_os_api.py`.
  - [ ] Return the fetched data (e.g., as a string or list/dict).
- [ ] **Implement `retrieve_security_zones` Tool (`server.py`):**
  - [ ] Define a Python function (e.g., `get_security_zones`).
  - [ ] Add the `@mcp.tool()` decorator.
  - [ ] Add type hints.
  - [ ] Call the corresponding function from `pan_os_api.py`.
  - [ ] Return the fetched data.
- [ ] **Implement `retrieve_security_policies` Tool (`server.py`):**
  - [ ] Define a Python function (e.g., `get_security_policies`).
  - [ ] Add the `@mcp.tool()` decorator.
  - [ ] Add type hints.
  - [ ] Call the corresponding function from `pan_os_api.py`.
  - [ ] Return the fetched data.
- [ ] **Implement Entry Point (`__main__.py`):**
  - [ ] Import the `mcp` instance from `server.py`.
  - [ ] Call `mcp.run()` to start the server using the default (stdio) transport.
- [ ] **Test Basic Execution:**
  - [ ] Run `uv run python -m palo_alto_mcp` locally (with dummy env vars if needed) to ensure it starts without immediate errors.

## Phase 3: Testing

- [ ] **Write Unit Tests (`tests/`):**
  - [ ] Test `pan_os_api.py` functions.
  - [ ] Mock `httpx` calls to simulate various API responses (success, errors, different XML structures).
  - [ ] Verify correct parsing of simulated XML responses.
  - [ ] Test API authentication logic.
  - [ ] Test configuration loading.
- [ ] **Write Integration Tests (`tests/`):**
  - [ ] Use `mcp.shared.memory.create_connected_server_and_client_session`.
  - [ ] Test `list_tools`: Verify all 3 tools are listed with correct names and generated schemas.
  - [ ] Test `call_tool` for `retrieve_address_objects`:
    - Mock the underlying API call within the tool function.
    - Verify the tool returns the expected data format (`TextContent`).
    - Test error propagation from the API client to the MCP response.
  - [ ] Test `call_tool` for `retrieve_security_zones` (similar approach).
  - [ ] Test `call_tool` for `retrieve_security_policies` (similar approach).
- [ ] **Run Code Quality Checks:**
  - [ ] Run `uv run ruff check . --fix` and `uv run ruff format .`.
  - [ ] Run `uv run pyright` (or `mypy`) and fix type errors.

## Phase 4: Documentation

- [ ] **Write `README.md`:**
  - [ ] Add Overview/Purpose section.
  - [ ] Add **Installation** instructions (using `uv pip install .` or `pip install .`).
  - [ ] Add **Configuration** instructions (list required Environment Variables: `PANOS_HOSTNAME`, `PANOS_API_KEY`).
  - [ ] Add **Usage** section (how to run it, how a client like Windsurf or `mcp install` would invoke it via command/args).
  - [ ] List **Available Tools** (`retrieve_address_objects`, etc.) and their purpose.

## Phase 5: Packaging & Release

- [ ] **Finalize `pyproject.toml`:**
  - [ ] Ensure all dependencies are listed correctly.
  - [ ] Verify package metadata.
  - [ ] Configure entry point script if desired (e.g., for a direct `palo-alto-mcp` command).
- [ ] **Build the Package:**
  - [ ] Run `uv build`.
- [ ] **Test Installation:**
  - [ ] Create a clean virtual environment.
  - [ ] Install the built wheel/sdist using `uv pip install dist/...`.
  - [ ] Verify the server can be run after installation.
- [ ] **Publish Package:**
  - [ ] Publish the built artifacts to the target Python package registry (e.g., PyPI).
