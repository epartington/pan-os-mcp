#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

// Path to the MCP server executable
const serverPath = path.join(__dirname, 'dist', 'index.js');

// Environment variables for testing
const testEnv = {
  ...process.env,
  PALO_ALTO_API_KEY: 'test-api-key',
  PALO_ALTO_API_URL: 'https://test-firewall.example.com/api',
  DEBUG: 'true'
};

// Spawn the MCP server process
const serverProcess = spawn('node', [serverPath], {
  stdio: ['pipe', 'pipe', 'pipe'],
  env: testEnv
});

// Handle server output
serverProcess.stdout.on('data', (data) => {
  console.log(`Server response: ${data}`);
  try {
    const response = JSON.parse(data.toString());
    console.log('Parsed response:', JSON.stringify(response, null, 2));
  } catch (error) {
    console.log('Could not parse response as JSON');
  }
});

serverProcess.stderr.on('data', (data) => {
  console.error(`Server error: ${data}`);
});

// Create a simple list_tools request
const listToolsRequest = {
  id: uuidv4(),
  method: 'list_tools',
  params: {}
};

// Send the request to the server
console.log('Sending list_tools request...');
serverProcess.stdin.write(JSON.stringify(listToolsRequest) + '\n');

// Wait for a moment and then test a tool call
setTimeout(() => {
  // Create a call_tool request for retrieve_address_objects
  const callToolRequest = {
    id: uuidv4(),
    method: 'call_tool',
    params: {
      name: 'retrieve_address_objects',
      params: {
        location: 'test-location',
        vsys: 'vsys1'
      }
    }
  };

  // Send the request to the server
  console.log('Sending call_tool request for retrieve_address_objects...');
  serverProcess.stdin.write(JSON.stringify(callToolRequest) + '\n');
}, 1000);

// Clean up when the process exits
process.on('SIGINT', () => {
  console.log('Terminating server process...');
  serverProcess.kill();
  process.exit(0);
});

// Auto-exit after 5 seconds
setTimeout(() => {
  console.log('Test completed, terminating server process...');
  serverProcess.kill();
  process.exit(0);
}, 5000);
