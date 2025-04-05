# Palo Alto MCP Server Development Guide

This document provides guidance for developers working on the Palo Alto MCP server project, including setup instructions, coding standards, and best practices.

## Development Environment Setup

### Prerequisites

- Node.js 18.x or later
- npm 8.x or later
- Access to a Palo Alto Networks firewall for testing (or mock API responses)

### Initial Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd palo-alto-mcp
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables for development:
   ```bash
   # Create a .env.dev file (not committed to version control)
   echo "PALO_ALTO_API_KEY=your-test-api-key" > .env.dev
   echo "PALO_ALTO_API_URL=https://your-test-firewall/api" >> .env.dev
   echo "DEBUG=true" >> .env.dev
   ```

4. Run in development mode:
   ```bash
   # Load environment variables and run
   source .env.dev && npm run dev
   ```

## Project Structure

The project follows the structure outlined in the PRD:

```
palo-alto-mcp/
├── src/
│   ├── index.ts              # Command-line entry point
│   ├── main.ts               # Main MCP server implementation
│   ├── init.ts               # Initialization and setup
│   ├── tools/                # Tool definitions
│   │   ├── address-objects.ts
│   │   ├── security-zones.ts
│   │   └── security-policies.ts
│   └── utils/                # Utilities
│       ├── helpers.ts        # Common utility functions
│       └── pan-os-api.ts     # API client for Palo Alto
├── tests/                    # Unit and integration tests
├── docs/                     # Documentation
│   ├── architecture.md       # Architectural design
│   ├── api-reference.md      # API reference
│   ├── client-connection.md  # Client connection guide
│   └── development-guide.md  # This file
├── package.json              # npm package definition
├── tsconfig.json             # TypeScript configuration
└── README.md                 # Project overview
```

## Development Workflow

### 1. Build and Run

```bash
# Build TypeScript to JavaScript
npm run build

# Run the built code
npm start

# Build and run in one step (development)
npm run dev
```

### 2. Testing

```bash
# Run all tests
npm test

# Run specific test file
npx vitest run tests/tools/address-objects.test.ts

# Run tests in watch mode
npx vitest watch
```

### 3. Linting and Formatting

```bash
# Lint code
npm run lint

# Format code
npm run format
```

## Adding New Features

### Adding a New Tool

1. Create a new file in `src/tools/` (e.g., `nat-rules.ts`)
2. Define the tool schema and handler:

```typescript
import { Tool } from '@modelcontextprotocol/sdk';
import { CallToolRequest } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { log, generateRequestId } from '../utils/helpers';
import { PanOsApiClient, LocationParamSchema, VsysParamSchema } from '../utils/pan-os-api';

// Define the tool schema
export const RETRIEVE_NAT_RULES_TOOL: Tool = {
  name: 'retrieve_nat_rules',
  description: 'Retrieve NAT rules from a Palo Alto Networks firewall',
  inputSchema: {
    type: 'object',
    properties: {
      location: {
        type: 'string',
        description: 'The hostname or IP address of the firewall',
      },
      vsys: {
        type: 'string',
        description: 'The virtual system name (default: vsys1)',
      },
    },
    required: ['location'],
  },
};

// Export all tools from this module
export const NAT_RULES_TOOLS = [RETRIEVE_NAT_RULES_TOOL];

// Parameter validation schema
const RetrieveNatRulesParamsSchema = z.object({
  location: LocationParamSchema,
  vsys: VsysParamSchema,
});

// Handler implementation
async function handleRetrieveNatRules(request: CallToolRequest) {
  // Implementation here
}

// Export all handlers from this module
export const NAT_RULES_HANDLERS: Record<string, Function> = {
  retrieve_nat_rules: handleRetrieveNatRules,
};
```

3. Add the PAN-OS API client method in `src/utils/pan-os-api.ts`
4. Register the tool in `src/main.ts`:

```typescript
import { NAT_RULES_HANDLERS, NAT_RULES_TOOLS } from './tools/nat-rules';

// Update ALL_TOOLS
const ALL_TOOLS = [
  ...ADDRESS_OBJECTS_TOOLS,
  ...SECURITY_ZONES_TOOLS,
  ...SECURITY_POLICIES_TOOLS,
  ...NAT_RULES_TOOLS, // Add the new tool
];

// Update tool handler routing in the CallToolRequestSchema handler
if (toolName in NAT_RULES_HANDLERS) {
  return await NAT_RULES_HANDLERS[toolName](request);
}
```

5. Add tests for the new tool in `tests/tools/nat-rules.test.ts`

### Extending the PAN-OS API Client

1. Add new interface definitions for API responses in `src/utils/pan-os-api.ts`
2. Add the new method to the `PanOsApiClient` class:

```typescript
/**
 * Retrieve NAT rules from the firewall
 */
async getNatRules(location: string, vsys: string = 'vsys1', requestId?: string): Promise<NatRulesResponse> {
  const params: Record<string, string> = {
    type: 'config',
    action: 'get',
    xpath: `/config/devices/entry[@name='${location}']/vsys/entry[@name='${vsys}']/rulebase/nat/rules`,
  };
  
  if (requestId) {
    params.requestId = requestId;
  }
  
  return this.makeRequest<NatRulesResponse>('api', params);
}
```

## Testing Strategy

### Unit Testing

- Test individual components in isolation
- Mock external dependencies (API calls)
- Focus on logic and error handling

Example unit test for a tool:

```typescript
import { describe, expect, it, vi } from 'vitest';
import { handleRetrieveAddressObjects } from '../../src/tools/address-objects';
import { PanOsApiClient } from '../../src/utils/pan-os-api';

// Mock PanOsApiClient
vi.mock('../../src/utils/pan-os-api', () => ({
  PanOsApiClient: vi.fn().mockImplementation(() => ({
    getAddressObjects: vi.fn().mockResolvedValue({
      status: 'success',
      result: {
        entry: [
          {
            '@name': 'test-address',
            'ip-netmask': '10.0.0.1/32',
            'description': 'Test address',
          }
        ]
      }
    })
  })),
  LocationParamSchema: { parse: vi.fn().mockReturnValue('10.1.1.1') },
  VsysParamSchema: { parse: vi.fn().mockReturnValue('vsys1') },
}));

describe('address-objects tool', () => {
  it('should retrieve address objects successfully', async () => {
    const request = {
      params: {
        name: 'retrieve_address_objects',
        parameters: {
          location: '10.1.1.1',
          vsys: 'vsys1'
        }
      }
    };
    
    const result = await handleRetrieveAddressObjects(request);
    
    expect(result).toHaveProperty('toolResult');
    expect(result.toolResult).toHaveProperty('content');
    expect(result.toolResult.content[0].type).toBe('text');
    
    const parsedContent = JSON.parse(result.toolResult.content[0].text);
    expect(parsedContent).toHaveLength(1);
    expect(parsedContent[0].name).toBe('test-address');
  });
});
```

### Integration Testing

- Test the interaction between components
- May use real API calls to a test firewall
- Focus on end-to-end workflows

Example integration test:

```typescript
import { describe, expect, it } from 'vitest';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js';

describe('MCP server integration', () => {
  let server: Server;
  
  beforeEach(() => {
    // Setup server for testing
    // ...
  });
  
  it('should handle list_tools request', async () => {
    const response = await server.handleRequest({
      jsonrpc: '2.0',
      method: 'list_tools',
      id: '1',
      params: {}
    });
    
    expect(response).toHaveProperty('result');
    expect(response.result).toHaveProperty('tools');
    expect(response.result.tools).toBeInstanceOf(Array);
  });
});
```

## Code Style and Standards

### TypeScript Best Practices

1. **Use Strong Typing**:
   - Avoid `any` type when possible
   - Define interfaces for all data structures
   - Use union types when appropriate

2. **Use ES2022 Features**:
   - Utilize modern JavaScript syntax
   - Use async/await for asynchronous operations
   - Use optional chaining (`?.`) and nullish coalescing (`??`)

3. **Error Handling**:
   - Use try/catch blocks for error handling
   - Provide informative error messages
   - Implement proper error propagation

### Naming Conventions

1. **File Names**: Use kebab-case for file names (e.g., `address-objects.ts`)
2. **Interfaces/Types**: Use PascalCase (e.g., `AddressObjectResponse`)
3. **Functions/Methods**: Use camelCase (e.g., `getAddressObjects`)
4. **Constants**: Use UPPER_SNAKE_CASE for true constants (e.g., `MAX_RETRY_COUNT`)

### Documentation

1. **JSDoc Comments**: Add JSDoc comments for all public methods and interfaces:

```typescript
/**
 * Retrieves address objects from the Palo Alto firewall
 * 
 * @param location - The hostname or IP address of the firewall
 * @param vsys - The virtual system name (default: vsys1)
 * @param requestId - Optional request ID for tracking in logs
 * @returns Promise resolving to the address objects response
 */
async getAddressObjects(location: string, vsys: string = 'vsys1', requestId?: string): Promise<AddressObjectResponse> {
  // ...
}
```

2. **Inline Comments**: Add comments for complex logic
3. **Markdown Documentation**: Update relevant markdown files when adding new features

## Performance Considerations

1. **Memory Usage**:
   - Be mindful of large response handling
   - Use streaming when appropriate for large datasets

2. **Async Operations**:
   - Use proper Promise handling
   - Consider concurrent requests when appropriate

3. **Error Recovery**:
   - Implement retry logic for transient errors
   - Set appropriate timeouts for network requests

## Security Best Practices

1. **Input Validation**:
   - Always validate input parameters with Zod
   - Sanitize inputs before using in API calls

2. **API Key Management**:
   - Never hardcode API keys
   - Use environment variables for sensitive data

3. **Error Messages**:
   - Don't expose sensitive information in error messages
   - Provide useful but safe error information

4. **Dependency Management**:
   - Regularly update dependencies
   - Use npm audit to check for vulnerabilities

## Release Process

1. **Version Bump**:
   - Update version in `package.json`
   - Follow semantic versioning (MAJOR.MINOR.PATCH)

2. **Building for Distribution**:
   ```bash
   npm run build
   ```

3. **Testing the Build**:
   ```bash
   npm test
   ```

4. **Publishing to npm**:
   ```bash
   npm publish
   ```

5. **Creating a Release**:
   - Tag the release in git
   - Create a GitHub release with release notes

## Resources

- [MCP SDK Documentation](https://github.com/modeldevelopment/mcp/tree/main/typescript/packages/sdk)
- [Palo Alto Networks API Documentation](https://docs.paloaltonetworks.com/pan-os/10-1/pan-os-panorama-api)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
