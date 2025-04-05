import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { log, validateConfig } from './utils/helpers';
import { PanOsApiClient } from './utils/pan-os-api';
import fs from 'fs';

// Helper for logging
const DEBUG = process.env.DEBUG === 'true';
function debug(...args: unknown[]): void {
  if (DEBUG) {
    const logPath = process.env.LOG_PATH || './mcp-server.log';
    const message = `[${new Date().toISOString()}] ${args
      .map((arg) => (typeof arg === 'object' ? JSON.stringify(arg) : arg))
      .join(' ')}\n`;

    fs.appendFileSync(logPath, message);
  }
}

// Create an MCP server
const server = new McpServer({
  name: 'palo-alto-mcp',
  version: '0.1.0',
});

debug('Server created');

// Add address objects tool
server.tool(
  'retrieve_address_objects',
  {
    location: z.string({ required_error: 'Location parameter is required' }),
    vsys: z.string().default('vsys1'),
  },
  async ({ location, vsys }) => {
    const requestId = 'req-' + Math.random().toString(36).substring(2, 10);
    debug('Called retrieve_address_objects', { location, vsys });
    log('Executing retrieve_address_objects', { location, vsys }, requestId);

    try {
      const client = new PanOsApiClient();

      // Retrieve address objects
      const response = await client.getAddressObjects(location, vsys, requestId);
      debug('Address objects result', response);

      // Format the response for MCP
      if (response.status === 'success') {
        const addressObjects = response.result.entry || [];

        // Transform into a more readable format for the client
        const formattedAddressObjects = addressObjects.map((entry) => ({
          name: entry['@name'],
          'ip-netmask': entry['ip-netmask'] || '',
          description: entry['description'] || '',
          // Infer type from the properties or use default
          type: entry['ip-netmask'] ? 'ip-netmask' : 'unknown',
        }));

        log(
          'Successfully retrieved address objects',
          { count: formattedAddressObjects.length },
          requestId
        );

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(formattedAddressObjects, null, 2),
            },
          ],
        };
      } else {
        throw new Error(`PAN-OS API error: ${response.message || 'Unknown error'}`);
      }
    } catch (error) {
      debug('Error in retrieve_address_objects', error);
      log('Error retrieving address objects', error, requestId);

      return {
        content: [
          {
            type: 'text',
            text: `Error: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// Add security zones tool
server.tool(
  'retrieve_security_zones',
  {
    location: z.string({ required_error: 'Location parameter is required' }),
    vsys: z.string().default('vsys1'),
  },
  async ({ location, vsys }) => {
    const requestId = 'req-' + Math.random().toString(36).substring(2, 10);
    debug('Called retrieve_security_zones', { location, vsys });
    log('Executing retrieve_security_zones', { location, vsys }, requestId);

    try {
      const client = new PanOsApiClient();

      // Retrieve security zones
      const response = await client.getSecurityZones(location, vsys, requestId);
      debug('Security zones result', response);

      // Format the response for MCP
      if (response.status === 'success') {
        const securityZones = response.result.entry || [];

        // Transform into a more readable format for the client
        const formattedSecurityZones = securityZones.map((entry) => ({
          name: entry['@name'],
          interfaces: entry.network?.layer3?.member || [],
        }));

        log(
          'Successfully retrieved security zones',
          { count: formattedSecurityZones.length },
          requestId
        );

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(formattedSecurityZones, null, 2),
            },
          ],
        };
      } else {
        throw new Error(`PAN-OS API error: ${response.message || 'Unknown error'}`);
      }
    } catch (error) {
      debug('Error in retrieve_security_zones', error);
      log('Error retrieving security zones', error, requestId);

      return {
        content: [
          {
            type: 'text',
            text: `Error: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// Add security policies tool
server.tool(
  'retrieve_security_policies',
  {
    location: z.string({ required_error: 'Location parameter is required' }),
    vsys: z.string().default('vsys1'),
  },
  async ({ location, vsys }) => {
    const requestId = 'req-' + Math.random().toString(36).substring(2, 10);
    debug('Called retrieve_security_policies', { location, vsys });
    log('Executing retrieve_security_policies', { location, vsys }, requestId);

    try {
      const client = new PanOsApiClient();

      // Retrieve security policies
      const response = await client.getSecurityPolicies(location, vsys, requestId);
      debug('Security policies result', response);

      // Format the response for MCP
      if (response.status === 'success') {
        const securityPolicies = response.result.entry || [];

        // Transform into a more readable format for the client
        const formattedSecurityPolicies = securityPolicies.map((entry) => ({
          name: entry['@name'],
          source_zones: entry.from?.member || [],
          destination_zones: entry.to?.member || [],
          source_addresses: entry.source?.member || [],
          services: entry.service?.member || [],
          action: entry.action || 'unknown',
        }));

        log(
          'Successfully retrieved security policies',
          { count: formattedSecurityPolicies.length },
          requestId
        );

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(formattedSecurityPolicies, null, 2),
            },
          ],
        };
      } else {
        throw new Error(`PAN-OS API error: ${response.message || 'Unknown error'}`);
      }
    } catch (error) {
      debug('Error in retrieve_security_policies', error);
      log('Error retrieving security policies', error, requestId);

      return {
        content: [
          {
            type: 'text',
            text: `Error: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// Start server
export async function main() {
  debug('Starting Palo Alto MCP server');
  log('Starting Palo Alto MCP server...');

  // Validate configuration
  if (!validateConfig()) {
    debug('Invalid configuration');
    log('Invalid configuration. Please set the required environment variables.');
    process.exit(1);
  }

  try {
    // Create standard I/O transport as specified in the PRD
    const transport = new StdioServerTransport();
    debug('Created standard I/O transport');
    log('Created standard I/O transport');

    // Connect the server to the transport
    await server.connect(transport);
    debug('Server connected and running');
    log('Server connected and running. Waiting for requests...');
  } catch (error) {
    debug('Fatal error:', error);
    log('Fatal error:', error);
    process.exit(1);
  }
}
