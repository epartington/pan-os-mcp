/**
 * Palo Alto Networks Firewall SDK client
 * Provides an abstraction layer for interacting with the PAN-OS API through the pan-os-typescript SDK
 */

import { Firewall, AddressObject, AddressType } from 'pan-os-typescript';
import { AddressObjectEntry } from 'pan-os-typescript/build/interfaces/AddressObjectResponse';
import { log } from './helpers';

// Define types for API responses
interface ApiResponse {
  result?: {
    entry?: unknown[];
  };
}

interface ApiEntry {
  $?: {
    name: string;
  };
  description?: string[];
  tag?: Array<{
    member?: string[];
  }>;
  [key: string]: unknown;
}

/**
 * PAN-OS SDK Client for interacting with the PAN-OS API
 */
export class PanOsSdkClient {
  private firewall: Firewall;

  /**
   * Creates a new PanOsSdkClient instance.
   *
   * @param apiUrl - The URL of the PAN-OS API
   * @param apiKey - The API key for authenticating with the PAN-OS API
   */
  constructor(apiUrl: string, apiKey: string) {
    // Extract hostname from URL
    const hostname = this.extractHostname(apiUrl);

    // Initialize the Firewall instance with hostname and API key
    this.firewall = new Firewall(hostname, apiKey);

    log(`Initialized PAN-OS SDK client for ${hostname}`);
  }

  /**
   * Extracts the hostname from a URL
   *
   * @param apiUrl - The URL to extract hostname from
   * @returns The extracted hostname
   */
  private extractHostname(apiUrl: string): string {
    try {
      const url = new URL(apiUrl);
      return url.hostname;
    } catch (error) {
      // If URL parsing fails, assume apiUrl is the hostname
      return apiUrl
        .replace(/^https?:\/\//, '')
        .split('/')[0]
        .split(':')[0];
    }
  }

  /**
   * Retrieves address objects from the firewall
   *
   * @param vsys - The virtual system to retrieve address objects from
   * @param requestId - Unique ID for request tracking
   * @returns Promise resolving to an array of address objects
   */
  public async getAddressObjects(
    vsys: string = 'vsys1',
    requestId?: string
  ): Promise<AddressObjectEntry[]> {
    try {
      log(`Retrieving address objects from vsys: ${vsys}`, undefined, requestId);

      // Use the SDK to get address objects via XPath query
      const xpath = AddressObject.getXpath().replace('vsys1', vsys);
      const response = await this.firewall.getConfig(xpath) as ApiResponse;

      // Check if we have valid entries
      if (response && response.result && response.result.entry) {
        const entries = Array.isArray(response.result.entry)
          ? response.result.entry
          : [response.result.entry];

        // Convert to normalized format using the SDK's interface
        return entries.map((entry) => this.mapToAddressObjectEntry(entry as ApiEntry));
      }

      return [];
    } catch (error) {
      log(
        `Error retrieving address objects`,
        { error: error instanceof Error ? error.message : String(error) },
        requestId
      );
      throw error;
    }
  }

  /**
   * Maps a raw API response to an AddressObjectEntry
   *
   * @param entry - The raw address object entry from the API
   * @returns An address object entry conforming to the SDK interface
   */
  private mapToAddressObjectEntry(entry: ApiEntry): AddressObjectEntry {
    const name = entry.$?.name || '';
    const type = this.getAddressObjectType(entry);
    const tags = entry.tag?.[0]?.member?.map((m) => m) || [];
    
    // Extract value based on the type
    let value = '';
    if (type && entry[type] && Array.isArray(entry[type])) {
      const valueArray = entry[type] as unknown[];
      if (valueArray.length > 0) {
        value = String(valueArray[0]);
      }
    }

    // Create the base object with common properties
    const addressEntry = {
      name,
      description: entry.description?.[0],
      tag: tags
    } as AddressObjectEntry;

    // Add the type-specific property in a type-safe manner
    // This approach leverages intersection types to add the property
    if (type === 'ip-netmask' && value) {
      return { ...addressEntry, 'ip-netmask': value };
    } else if (type === 'ip-range' && value) {
      return { ...addressEntry, 'ip-range': value };
    } else if (type === 'fqdn' && value) {
      return { ...addressEntry, fqdn: value };
    } else if (type === 'ip-wildcard' && value) {
      // For ip-wildcard, we need to be careful since it might not be in the interface
      // Return a merged object, cast to the right type
      return { ...addressEntry, [type]: value } as AddressObjectEntry;
    }

    // Default case - return with the most common type (ip-netmask)
    return { ...addressEntry, 'ip-netmask': value || '' };
  }

  /**
   * Determines the address object type from the API response
   *
   * @param entry - The raw address object entry
   * @returns The address object type
   */
  private getAddressObjectType(entry: ApiEntry): AddressType {
    const possibleTypes: AddressType[] = ['ip-netmask', 'ip-range', 'ip-wildcard', 'fqdn'];

    for (const type of possibleTypes) {
      if (entry[type]) {
        return type;
      }
    }

    return 'ip-netmask'; // Default type
  }
}
