import { Tool } from '@modelcontextprotocol/sdk';
import { CallToolRequest } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { log, generateRequestId } from '../utils/helpers';
import { PanOsApiClient, LocationParamSchema, VsysParamSchema } from '../utils/pan-os-api';

// Define the tool schema
export const RETRIEVE_SECURITY_POLICIES_TOOL: Tool = {
  name: 'retrieve_security_policies',
  description: 'Retrieve security policies from a Palo Alto Networks firewall',
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
export const SECURITY_POLICIES_TOOLS = [RETRIEVE_SECURITY_POLICIES_TOOL];

// Parameter validation schema
const RetrieveSecurityPoliciesParamsSchema = z.object({
  location: LocationParamSchema,
  vsys: VsysParamSchema,
});

// Handler implementation
async function handleRetrieveSecurityPolicies(request: CallToolRequest) {
  const requestId = generateRequestId();
  log('Executing retrieve_security_policies', request.params, requestId);

  try {
    // Validate parameters
    const { location, vsys } = RetrieveSecurityPoliciesParamsSchema.parse(request.params);
    
    // Create PAN-OS API client
    const client = new PanOsApiClient();
    
    // Retrieve security policies
    const response = await client.getSecurityPolicies(location, vsys, requestId);
    
    // Format the response for MCP
    if (response.status === 'success') {
      const securityPolicies = response.result.entry || [];
      
      // Transform into a more readable format for the client
      const formattedSecurityPolicies = securityPolicies.map(entry => ({
        name: entry['@name'],
        source_zones: entry.from?.member || [],
        destination_zones: entry.to?.member || [],
        source_addresses: entry.source?.member || [],
        destination_addresses: entry.destination?.member || [],
        applications: entry.application?.member || [],
        services: entry.service?.member || [],
        action: entry.action || 'unknown',
      }));
      
      log('Successfully retrieved security policies', { count: formattedSecurityPolicies.length }, requestId);
      
      return {
        toolResult: {
          content: [
            {
              type: 'text',
              text: JSON.stringify(formattedSecurityPolicies, null, 2),
            },
          ],
        },
      };
    } else {
      throw new Error(`PAN-OS API error: ${response.message || 'Unknown error'}`);
    }
  } catch (error) {
    log('Error retrieving security policies', error, requestId);
    
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
export const SECURITY_POLICIES_HANDLERS: Record<string, Function> = {
  retrieve_security_policies: handleRetrieveSecurityPolicies,
};
