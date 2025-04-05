import { Tool } from '@modelcontextprotocol/sdk';
import { CallToolRequest } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { log, generateRequestId } from '../utils/helpers';
import { PanOsApiClient, LocationParamSchema, VsysParamSchema } from '../utils/pan-os-api';

// Define the tool schema
export const RETRIEVE_ADDRESS_OBJECTS_TOOL: Tool = {
  name: 'retrieve_address_objects',
  description: 'Retrieve address objects from a Palo Alto Networks firewall',
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
export const ADDRESS_OBJECTS_TOOLS = [RETRIEVE_ADDRESS_OBJECTS_TOOL];

// Parameter validation schema
const RetrieveAddressObjectsParamsSchema = z.object({
  location: LocationParamSchema,
  vsys: VsysParamSchema,
});

// Handler implementation
async function handleRetrieveAddressObjects(request: CallToolRequest) {
  const requestId = generateRequestId();
  log('Executing retrieve_address_objects', request.params, requestId);

  try {
    // Validate parameters
    const { location, vsys } = RetrieveAddressObjectsParamsSchema.parse(request.params);
    
    // Create PAN-OS API client
    const client = new PanOsApiClient();
    
    // Retrieve address objects
    const response = await client.getAddressObjects(location, vsys, requestId);
    
    // Format the response for MCP
    if (response.status === 'success') {
      const addressObjects = response.result.entry || [];
      
      // Transform into a more readable format for the client
      const formattedAddressObjects = addressObjects.map(entry => ({
        name: entry['@name'],
        'ip-netmask': entry['ip-netmask'] || '',
        description: entry['description'] || '',
        tags: entry['tag']?.member || [],
      }));
      
      log('Successfully retrieved address objects', { count: formattedAddressObjects.length }, requestId);
      
      return {
        toolResult: {
          content: [
            {
              type: 'text',
              text: JSON.stringify(formattedAddressObjects, null, 2),
            },
          ],
        },
      };
    } else {
      throw new Error(`PAN-OS API error: ${response.message || 'Unknown error'}`);
    }
  } catch (error) {
    log('Error retrieving address objects', error, requestId);
    
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
export const ADDRESS_OBJECTS_HANDLERS: Record<string, Function> = {
  retrieve_address_objects: handleRetrieveAddressObjects,
};
