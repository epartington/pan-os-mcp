import { McpClient } from '@modelcontextprotocol/sdk/client/mcp.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

async function main() {
  try {
    console.log('Creating MCP client to test the dev_show_system_info_ tool...');
    
    // Create a client and connect to the server via stdio
    const transport = new StdioClientTransport();
    const client = new McpClient();
    await client.connect(transport);
    
    console.log('Connected to MCP server. Calling dev_show_system_info_ tool...');
    
    // Call our mock system info tool
    const response = await client.callTool('dev_show_system_info_', {});
    
    // Print the response
    console.log('\nResponse from dev_show_system_info_ tool:');
    
    // Check if we have content
    if (response && response.content && response.content.length > 0) {
      // Parse the JSON text content to make it pretty
      const textContent = response.content[0];
      if (textContent && textContent.type === 'text') {
        try {
          const systemInfo = JSON.parse(textContent.text);
          console.log(JSON.stringify(systemInfo, null, 2));
        } catch (e) {
          console.log(textContent.text);
        }
      } else {
        console.log(response);
      }
    } else {
      console.log('No content in response:', response);
    }
    
    // Disconnect from the server
    await client.disconnect();
    console.log('\nTest completed successfully!');
    
    // Exit process
    process.exit(0);
  } catch (error) {
    console.error('Error testing tool:', error);
    process.exit(1);
  }
}

// Run the main function
main();
