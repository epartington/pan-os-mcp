# TODO List: MCP Palo Alto Integration Server (Python SDK)

## Phase 1: Project Setup & API Client (Completed)

- [x] **Initialize Project Environment:**
  - [x] Create the main project directory (`palo-alto-mcp`).
  - [x] Initialize the project using `uv init`.
  - [x] Set up the basic directory structure:
    - `src/palo_alto_mcp/`
    - `tests/`
- [x] **Configure `pyproject.toml`:**
  - [x] Define project metadata (name, version source, authors, etc.).
  - [x] Add core dependencies: `mcp`, `httpx`.
  - [x] Add optional dependencies if using: `pydantic-settings`.
  - [x] Add development dependencies: `pytest`, `ruff`, `pyright`/`mypy`.
  - [x] Configure build system (`hatchling`, `uv-dynamic-versioning`).
  - [x] Configure linters/formatters (`ruff`, `pyright`).
- [x] **Create Basic Python Files:**
  - [x] `src/palo_alto_mcp/__init__.py` (can be empty).
  - [x] `src/palo_alto_mcp/pan_os_api.py` (for API client logic).
  - [x] `src/palo_alto_mcp/server.py` (for `FastMCP` implementation).
  - [x] `src/palo_alto_mcp/__main__.py` (for entry point).
- [x] **Implement Configuration Loading:**
  - [x] Define required environment variables (`PANOS_HOSTNAME`, `PANOS_API_KEY`).
  - [x] Implement loading using `pydantic-settings` in a dedicated `config.py`.
- [x] **Implement Palo Alto API Client (`pan_os_api.py`):**
  - [x] Implement connection logic using `httpx` (HTTPS, base URL from config).
  - [x] Implement authentication logic using API key (from config).
  - [x] Implement function to fetch System Information.
  - [x] Implement function to fetch Address Objects (send request, handle XML response).
  - [x] Implement function to fetch Security Zones (send request, handle XML response).
  - [x] Implement function to fetch Security Policies (send request, handle XML response).
  - [x] Implement basic error handling for API requests (e.g., connection errors, auth failures, non-200 responses).
  - [x] Add support for Panorama device groups and shared objects.

## Phase 2: `FastMCP` Server Implementation (Completed)

- [x] **Instantiate `FastMCP` (`server.py`):**
  - [x] Import `FastMCP` from `mcp.server.fastmcp`.
  - [x] Create an instance: `mcp = FastMCP("PaloAltoMCPServer", ...)`.
  - [x] Load configuration (hostname, API key) needed by tools.
- [x] **Implement `show_system_info` Tool (`server.py`):**
  - [x] Define a Python function.
  - [x] Add the `@mcp.tool()` decorator.
  - [x] Add type hints for any arguments (if required) and the return value.
  - [x] Call the corresponding function from `pan_os_api.py`.
  - [x] Return the fetched data as formatted text.
- [x] **Implement `retrieve_address_objects` Tool (`server.py`):**
  - [x] Define a Python function.
  - [x] Add the `@mcp.tool()` decorator.
  - [x] Add type hints.
  - [x] Call the corresponding function from `pan_os_api.py`.
  - [x] Return the fetched data as formatted text.
  - [x] Group objects by location (shared, device group, vsys).
- [x] **Implement `retrieve_security_zones` Tool (`server.py`):**
  - [x] Define a Python function.
  - [x] Add the `@mcp.tool()` decorator.
  - [x] Add type hints.
  - [x] Call the corresponding function from `pan_os_api.py`.
  - [x] Return the fetched data as formatted text.
- [x] **Implement `retrieve_security_policies` Tool (`server.py`):**
  - [x] Define a Python function.
  - [x] Add the `@mcp.tool()` decorator.
  - [x] Add type hints.
  - [x] Call the corresponding function from `pan_os_api.py`.
  - [x] Return the fetched data as formatted text.
- [x] **Implement Entry Point (`__main__.py`):**
  - [x] Import the `mcp` instance from `server.py`.
  - [x] Call `mcp.run(transport="sse")` to start the server using SSE transport.
- [x] **Test Basic Execution:**
  - [x] Run `python -m palo_alto_mcp` locally to ensure it starts without immediate errors.

## Phase 3: Testing and Documentation (In Progress)

- [ ] **Write Unit Tests (`tests/`):**
  - [ ] Test `pan_os_api.py` functions.
  - [ ] Mock `httpx` calls to simulate various API responses (success, errors, different XML structures).
  - [ ] Verify correct parsing of simulated XML responses.
  - [ ] Test API authentication logic.
  - [ ] Test configuration loading.
- [ ] **Write Integration Tests (`tests/`):**
  - [ ] Use `mcp.shared.memory.create_connected_server_and_client_session`.
  - [ ] Test `list_tools`: Verify all tools are listed with correct names and generated schemas.
  - [ ] Test `call_tool` for each of the implemented tools.
  - [ ] Mock the underlying API calls within the tool functions.
  - [ ] Verify the tools return the expected data format (`TextContent`).
  - [ ] Test error propagation from the API client to the MCP response.
- [x] **Run Code Quality Checks:**
  - [x] Run linting and fix issues.
  - [x] Run type checking and fix type errors.
- [x] **Write `README.md`:**
  - [x] Add Overview/Purpose section.
  - [x] Add **Installation** instructions (using `uv pip install .` or `pip install .`).
  - [x] Add **Configuration** instructions (list required Environment Variables: `PANOS_HOSTNAME`, `PANOS_API_KEY`).
  - [x] Add **Usage** section (how to run it, how clients can connect via SSE).
  - [x] List **Available Tools** and their purpose with example responses.
- [x] **Update PRD.md to reflect current implementation:**
  - [x] Update scope with Panorama support.
  - [x] Update transport mechanism details (SSE).
  - [x] Update requirements to match the current implementation.
  - [x] Update user stories and acceptance criteria.

## Phase 4: Release (Pending)

- [ ] **Finalize `pyproject.toml`:**
  - [ ] Ensure all dependencies are listed correctly.
  - [ ] Verify package metadata.
  - [ ] Configure entry point script for a direct `palo-alto-mcp` command.
- [ ] **Build the Package:**
  - [ ] Run `uv build`.
- [ ] **Test Installation:**
  - [ ] Create a clean virtual environment.
  - [ ] Install the built wheel/sdist using `uv pip install dist/...`.
  - [ ] Verify the server can be run after installation.
- [ ] **Publish Package:**
  - [ ] Publish the built artifacts to the target Python package registry (e.g., PyPI).

## Phase 5: Future Enhancements

- [ ] **Additional Tools:**
  - [ ] Add tool for retrieving NAT policies.
  - [ ] Add tool for retrieving interface configurations.
  - [ ] Add tool for retrieving application objects.
  - [ ] Add tool for retrieving service objects.
- [ ] **Performance Improvements:**
  - [ ] Implement caching for API responses.
  - [ ] Add concurrency for fetching multiple object types simultaneously.
- [ ] **Security Enhancements:**
  - [ ] Implement proper SSL certificate verification.
  - [ ] Add support for alternative authentication methods.
- [ ] **Usability Improvements:**
  - [ ] Add filtering capabilities to tools (e.g., filter by name pattern).
  - [ ] Enhance error messages and logging.
  - [ ] Add progress reporting for long-running operations.
- [ ] **Configuration Management:**
  - [ ] Add tools for modifying/creating firewall configurations.
  - [ ] Implement validation and safety checks for configuration changes.
  - [ ] Add commit/rollback functionality.