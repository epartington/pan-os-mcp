import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

// Create a dummy server
const server = new McpServer({ name: 'test-server', version: '0.0.1' });

// This function will show us what properties are available in the tool handler
server.tool('test_tool', (extra) => {
  console.log('Properties available on extra:', Object.keys(extra));
  return {
    content: [{
      type: 'text',
      text: 'This is a test'
    }]
  };
});

console.log('Created test server');
