import { Tool } from '@modelcontextprotocol/sdk';
import { CallToolRequest } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { log, generateRequestId } from '../utils/helpers';
import { PanOsApiClient, LocationParamSchema, VsysParamSchema } from '../utils/pan-os-api';

// Define the tool schema
export const RETRIEVE_SECURITY_ZONES_TOOL: Tool = {
  name: 'retrieve_security_zones',
  description: 'Retrieve security zones from a Palo Alto Networks firewall',
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
export const SECURITY_ZONES_TOOLS = [RETRIEVE_SECURITY_ZONES_TOOL];

// Parameter validation schema
const RetrieveSecurityZonesParamsSchema = z.object({
  location: LocationParamSchema,
  vsys: VsysParamSchema,
});

// Handler implementation
async function handleRetrieveSecurityZones(request: CallToolRequest) {
  const requestId = generateRequestId();
  log('Executing retrieve_security_zones', request.params, requestId);

  try {
    // Validate parameters
    const { location, vsys } = RetrieveSecurityZonesParamsSchema.parse(request.params);
    
    // Create PAN-OS API client
    const client = new PanOsApiClient();
    
    // Retrieve security zones
    const response = await client.getSecurityZones(location, vsys, requestId);
    
    // Format the response for MCP
    if (response.status === 'success') {
      const securityZones = response.result.entry || [];
      
      // Transform into a more readable format for the client
      const formattedSecurityZones = securityZones.map(entry => ({
        name: entry['@name'],
        interfaces: entry.network?.layer3?.member || [],
      }));
      
      log('Successfully retrieved security zones', { count: formattedSecurityZones.length }, requestId);
      
      return {
        toolResult: {
          content: [
            {
              type: 'text',
              text: JSON.stringify(formattedSecurityZones, null, 2),
            },
          ],
        },
      };
    } else {
      throw new Error(`PAN-OS API error: ${response.message || 'Unknown error'}`);
    }
  } catch (error) {
    log('Error retrieving security zones', error, requestId);
    
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
}

// Export all handlers from this module
export const SECURITY_ZONES_HANDLERS: Record<string, Function> = {
  retrieve_security_zones: handleRetrieveSecurityZones,
};
