import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { log, validateConfig, config } from './utils/helpers';
import { PanOsSdkClient } from './utils/pan-os-sdk-client';
import fs from 'fs';
import { Firewall } from 'pan-os-typescript';

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

            // Check if we're in development mode
            if (config.devMode) {
              log(
                'Running in development mode - returning mock address objects',
                undefined,
                requestId
              );
              return {
                content: [
                  {
                    type: 'text',
                    text: JSON.stringify(
                      [
                        {
                          name: 'test-address-1',
                          'ip-netmask': '192.168.1.0/24',
                          description: 'Test address object 1',
                          tag: ['dev', 'test'],
                        },
                        {
                          name: 'test-address-2',
                          'ip-netmask': '10.0.0.0/8',
                          description: 'Test address object 2',
                          tag: ['internal'],
                        },
                      ],
                      null,
                      2
                    ),
                  },
                ],
              };
            }

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

    // Actual show_system_info tool that uses the pan-os-typescript SDK to connect to a real firewall
    server.tool('show_system_info', function () {
      try {
        // Create a unique request ID for this call
        const requestId = `sysinfo-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;

        return (async () => {
          try {
            // Get API key and hostname from environment variables
            const apiKey = process.env.PANOS_API_KEY;
            const hostname = process.env.PANOS_HOSTNAME || 'localhost';

            if (!apiKey) {
              throw new Error('Missing required environment variable: PANOS_API_KEY');
            }

            log('Connecting to firewall to retrieve system info', { hostname }, requestId);

            // Initialize the Firewall client from the SDK
            const firewall = new Firewall(hostname, apiKey);

            // Fetch the system information from the PAN-OS device
            const systemInfo = await firewall.showSystemInfoResponse();

            log('Successfully retrieved system info from firewall', undefined, requestId);

            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(systemInfo, null, 2),
                },
              ],
            };
          } catch (error) {
            log('Error retrieving system info from firewall', error, requestId);
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

    // Mock system info tool - returns pre-defined mock data like the actual System Info response
    server.tool('dev_show_system_info', function () {
      try {
        // Create a unique request ID for this call
        const requestId = `mock-sysinfo-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;

        return (async () => {
          try {
            // Current timestamp in ISO format
            const timestamp = new Date().toISOString();

            // Mock system info that matches the example output
            const mockSystemInfo = {
              result: {
                system: {
                  'advanced-routing': 'off',
                  'app-release-date': '2024/12/12 17:24:38 CST',
                  'app-version': '8924-9120',
                  'av-release-date': '2024/12/16 06:03:43 CST',
                  'av-version': '5034-5552',
                  'cloud-mode': 'non-cloud',
                  'default-gateway': '10.0.0.1',
                  'device-certificate-status': 'Valid',
                  'device-dictionary-release-date': '2025/03/29 19:27:38 CDT',
                  'device-dictionary-version': '168-589',
                  devicename: 'dallas',
                  'duplicate-ip': 'Disabled',
                  family: 'vm',
                  'global-protect-client-package-version': '0.0.0',
                  'global-protect-clientless-vpn-version': '0',
                  'global-protect-datafile-release-date': 'unknown',
                  'global-protect-datafile-version': '0',
                  hostname: 'dallas',
                  'ip-address': '10.0.0.202',
                  'ipv6-address': 'unknown',
                  'ipv6-link-local-address': 'fe80::be24:11ff:fe36:72e6/64',
                  'is-dhcp': 'no',
                  'is-dhcp6': 'no',
                  'logdb-version': '11.1.0',
                  'mac-address': 'bc:24:11:36:72:e6',
                  model: 'PA-VM',
                  'multi-vsys': 'off',
                  netmask: '255.255.255.0',
                  'operational-mode': 'normal',
                  'platform-family': 'vm',
                  plugin_versions: {
                    entry: [
                      { pkginfo: 'dlp-5.0.1' },
                      { pkginfo: 'openconfig-2.0.2-c50.dev' },
                      { pkginfo: 'vm_series-5.0.3' },
                    ],
                  },
                  'public-ip-address': 'unknown',
                  relicense: '0',
                  serial: '007954000543268',
                  'sw-version': '11.1.4',
                  'threat-release-date': '2024/12/12 17:24:38 CST',
                  'threat-version': '8924-9120',
                  time: `${new Date().toDateString()} ${new Date().toTimeString().split(' ')[0]}\n`,
                  uptime: '80 days, 20:57:19',
                  'url-db': 'paloaltonetworks',
                  'url-filtering-version': '20250327.20089',
                  'vm-cap-tier': 'T2-10GB',
                  'vm-cores': '4',
                  'vm-cpuid': 'KVM:ED060900FFFB8B0F',
                  'vm-license': 'VM-SERIES-4',
                  'vm-mac-base': '7C:89:C3:DD:A4:00',
                  'vm-mac-count': '256',
                  'vm-mem': '11254476',
                  'vm-mode': 'KVM',
                  'vm-uuid': 'E0314B74-EB3D-4BCB-8B28-5FCF8ABA8E24',
                  'vpn-disable-mode': 'off',
                  'wf-private-release-date': 'unknown',
                  'wf-private-version': '0',
                  'wildfire-release-date': '2024/12/16 07:42:13 CST',
                  'wildfire-rt': 'Disabled',
                  'wildfire-version': '935313-939246',
                },
              },
              timestamp,
            };

            log('Returning mock system info', undefined, requestId);

            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(mockSystemInfo, null, 2),
                },
              ],
            };
          } catch (error) {
            log('Error in mock system info', error, requestId);
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
