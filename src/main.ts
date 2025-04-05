import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { log, validateConfig } from './utils/helpers';
import { 
  ADDRESS_OBJECTS_HANDLERS, 
  ADDRESS_OBJECTS_TOOLS 
} from './tools/address-objects';
import { 
  SECURITY_ZONES_HANDLERS, 
  SECURITY_ZONES_TOOLS 
} from './tools/security-zones';
import { 
  SECURITY_POLICIES_HANDLERS, 
  SECURITY_POLICIES_TOOLS 
} from './tools/security-policies';

// Combine all tools
const ALL_TOOLS = [
  ...ADDRESS_OBJECTS_TOOLS,
  ...SECURITY_ZONES_TOOLS,
  ...SECURITY_POLICIES_TOOLS,
];

// Create an MCP server
const server = new Server(
  { name: 'palo-alto-mcp', version: '0.1.0' },
  { capabilities: { tools: {} } },
);

// Handle list tools request
server.setRequestHandler(ListToolsRequestSchema, async () => {
  log('Received list tools request');
  return { tools: ALL_TOOLS };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const toolName = request.params.name;
  log('Received tool call:', toolName);

  try {
    if (toolName in ADDRESS_OBJECTS_HANDLERS) {
      return await ADDRESS_OBJECTS_HANDLERS[toolName](request);
    }
    if (toolName in SECURITY_ZONES_HANDLERS) {
      return await SECURITY_ZONES_HANDLERS[toolName](request);
    }
    if (toolName in SECURITY_POLICIES_HANDLERS) {
      return await SECURITY_POLICIES_HANDLERS[toolName](request);
    }

    throw new Error(`Unknown tool: ${toolName}`);
  } catch (error) {
    log('Error handling tool call:', error);
    return {
      toolResult: {
        content: [
          {
            type: 'text',
            text: `Error: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      },
    };
  }
});

// Start server
export async function main() {
  log('Starting Palo Alto MCP server...');
  
  // Validate configuration
  if (!validateConfig()) {
    log('Invalid configuration. Please set the required environment variables.');
    process.exit(1);
  }
  
  try {
    // Create standard I/O transport as specified in the PRD
    const transport = new StdioServerTransport();
    log('Created standard I/O transport');
    
    // Connect the server to the transport
    await server.connect(transport);
    log('Server connected and running. Waiting for requests...');
  } catch (error) {
    log('Fatal error:', error);
    process.exit(1);
  }
}
