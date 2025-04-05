import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { log, validateConfig } from './utils/helpers';
import { PanOsSdkClient } from './utils/pan-os-sdk-client';
import fs from 'fs';

// Helper for logging
const DEBUG = process.env.DEBUG === 'true';
function debug(...args: unknown[]): void {
  if (DEBUG) {
    const logPath = process.env.LOG_PATH || './mcp-server.log';
    const message = `[${new Date().toISOString()}] ${args
      .map((arg) => (typeof arg === 'object' ? JSON.stringify(arg) : arg))
      .join(' ')}`;
    fs.appendFileSync(logPath, message + '\n');
  }
}

// Validate Zod schemas
const LocationSchema = z.object({
  location: z.string().optional(),
  vsys: z.string().optional(),
});

/**
 * Main function to start the MCP server
 */
export async function main(): Promise<void> {
  try {
    log('Starting Palo Alto MCP server...');

    // Validate configuration
    if (!validateConfig()) {
      process.exit(1);
    }

    // Create a server
    const server = new McpServer({
      name: 'palo-alto-mcp',
      version: '0.1.0',
    });

    // Register tools using the correct format for the MCP SDK
    server.tool('retrieve_address_objects', function (extra) {
      try {
        // Create a unique request ID for this call
        const requestId = `addr-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;

        return (async () => {
          try {
            // Extract parameters, handle SDK version differences
            const params = typeof extra === 'object' ? (extra as Record<string, unknown>) : {};

            // Parse and validate input using Zod
            const { vsys = 'vsys1' } = LocationSchema.parse(params);

            // Get API key and URL from environment variables
            const apiKey = process.env.PALO_ALTO_API_KEY;
            const apiUrl = process.env.PALO_ALTO_API_URL;

            if (!apiKey || !apiUrl) {
              throw new Error(
                'Missing required environment variables: PALO_ALTO_API_KEY, PALO_ALTO_API_URL'
              );
            }

            // Create PAN-OS SDK client
            const panOsClient = new PanOsSdkClient(apiUrl, apiKey);

            // Get address objects
            const addressObjects = await panOsClient.getAddressObjects(vsys, requestId);

            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(addressObjects, null, 2),
                },
              ],
            };
          } catch (error) {
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
        })();
      } catch (error) {
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
    });

    // NOTE: Security zones and policies functionality has been removed from the SDK client
    // to focus only on address objects for now.
    /*
    server.tool('retrieve_security_zones', function (extra) {
      // Implementation removed
    });

    server.tool('retrieve_security_policies', function (extra) {
      // Implementation removed
    });
    */

    // Create a standard I/O transport for the server
    const transport = new StdioServerTransport();

    // Connect to the transport
    log('Created standard I/O transport');
    await server.connect(transport);

    // Start serving requests
    log('Server connected and running. Waiting for requests...');
    // The SDK does not have a serve() method, it automatically starts serving
    // after connect().
  } catch (error) {
    debug('Fatal error:', error);
    log('Fatal error:', error);
    process.exit(1);
  }
}

// Run the main function if this module is being run directly
if (require.main === module) {
  main();
}
