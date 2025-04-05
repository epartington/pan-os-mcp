import { fetch } from 'undici';
import { log, config } from './helpers';
import { z } from 'zod';

// Define common validation schemas
export const LocationParamSchema = z.string({
  required_error: 'Location parameter is required',
  invalid_type_error: 'Location must be a string',
});

export const VsysParamSchema = z
  .string({
    required_error: 'Vsys parameter is required',
    invalid_type_error: 'Vsys must be a string',
  })
  .default('vsys1');

// Define common interfaces for PAN-OS API
interface PanOsApiResponse {
  status: 'success' | 'error';
  code?: number;
  message?: string;
}

interface AddressObjectResponse extends PanOsApiResponse {
  result: {
    entry?: Array<{
      '@name': string;
      'ip-netmask'?: string;
      description?: string;
      tag?: { member?: string[] };
      // Add other address object fields as needed
    }>;
  };
}

interface SecurityZoneResponse extends PanOsApiResponse {
  result: {
    entry?: Array<{
      '@name': string;
      network?: {
        layer3?: {
          member?: string[];
        };
      };
      // Add other security zone fields as needed
    }>;
  };
}

interface SecurityPolicyResponse extends PanOsApiResponse {
  result: {
    entry?: Array<{
      '@name': string;
      from?: { member?: string[] };
      to?: { member?: string[] };
      source?: { member?: string[] };
      destination?: { member?: string[] };
      application?: { member?: string[] };
      service?: { member?: string[] };
      action?: string;
      // Add other security policy fields as needed
    }>;
  };
}

/**
 * PAN-OS API Client for Palo Alto Networks NGFW
 */
export class PanOsApiClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;

  constructor(apiKey: string = config.apiKey, baseUrl: string = config.apiUrl) {
    if (!apiKey) {
      throw new Error('API key is required');
    }
    if (!baseUrl) {
      throw new Error('API URL is required');
    }
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;
  }

  /**
   * Make a generic API request to the PAN-OS XML API
   */
  private async makeRequest<T>(
    endpoint: string,
    params: Record<string, string> = {},
    reqId?: string
  ): Promise<T> {
    try {
      // Use the provided request ID or generate a default one
      const requestId = reqId || 'api-' + Math.random().toString(36).substring(2, 10);

      const queryParams = new URLSearchParams({
        key: this.apiKey,
        ...params,
      });

      const url = `${this.baseUrl}${endpoint}?${queryParams.toString()}`;

      log(`Making request to PAN-OS API: ${endpoint}`, { params }, requestId);

      const response = await fetch(url);

      if (!response.ok) {
        const errorText = await response.text();
        log(
          `PAN-OS API error: ${response.status} ${response.statusText}`,
          { error: errorText },
          requestId
        );
        throw new Error(`PAN-OS API error: ${response.status} ${response.statusText}`);
      }

      const data = (await response.json()) as T;
      log(`PAN-OS API response received`, undefined, requestId);
      return data;
    } catch (error) {
      log(
        `PAN-OS API request failed`,
        { error: error instanceof Error ? error.message : String(error) },
        reqId
      );
      throw error;
    }
  }

  /**
   * Retrieve address objects from the firewall
   */
  async getAddressObjects(
    location: string,
    vsys: string = 'vsys1',
    requestId?: string
  ): Promise<AddressObjectResponse> {
    const params: Record<string, string> = {
      type: 'config',
      action: 'get',
      xpath: `/config/devices/entry[@name='${location}']/vsys/entry[@name='${vsys}']/address`,
    };

    if (requestId) {
      params.requestId = requestId;
    }

    return this.makeRequest<AddressObjectResponse>('api', params);
  }

  /**
   * Retrieve security zones from the firewall
   */
  async getSecurityZones(
    location: string,
    vsys: string = 'vsys1',
    requestId?: string
  ): Promise<SecurityZoneResponse> {
    const params: Record<string, string> = {
      type: 'config',
      action: 'get',
      xpath: `/config/devices/entry[@name='${location}']/vsys/entry[@name='${vsys}']/zone`,
    };

    if (requestId) {
      params.requestId = requestId;
    }

    return this.makeRequest<SecurityZoneResponse>('api', params);
  }

  /**
   * Retrieve security policies from the firewall
   */
  async getSecurityPolicies(
    location: string,
    vsys: string = 'vsys1',
    requestId?: string
  ): Promise<SecurityPolicyResponse> {
    const params: Record<string, string> = {
      type: 'config',
      action: 'get',
      xpath: `/config/devices/entry[@name='${location}']/vsys/entry[@name='${vsys}']/rulebase/security/rules`,
    };

    if (requestId) {
      params.requestId = requestId;
    }

    return this.makeRequest<SecurityPolicyResponse>('api', params);
  }
}
