import { describe, it, expect, vi, beforeEach, afterAll } from 'vitest';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

// Save the original process.exit
const originalProcessExit = process.exit;

// Mock the modules
vi.mock('@modelcontextprotocol/sdk/server/mcp.js', () => {
  return {
    McpServer: vi.fn().mockImplementation(() => ({
      tool: vi.fn(),
      connect: vi.fn().mockResolvedValue(undefined),
      serve: vi.fn().mockResolvedValue(undefined),
    })),
  };
});

vi.mock('@modelcontextprotocol/sdk/server/stdio.js', () => {
  return {
    StdioServerTransport: vi.fn().mockImplementation(() => ({})),
  };
});

// Set up and restore mocks
beforeEach(() => {
  // Mock process.exit
  process.exit = vi.fn() as any;
  
  // Reset environment variables
  process.env.PALO_ALTO_API_KEY = 'test-api-key';
  process.env.PALO_ALTO_API_URL = 'https://test-firewall.example.com/api';
  
  // Clear mock history
  vi.clearAllMocks();
});

// Restore original process.exit after tests
afterAll(() => {
  process.exit = originalProcessExit;
});

// Mock the helpers function
vi.mock('../src/utils/helpers', () => ({
  log: vi.fn(),
  validateConfig: vi.fn().mockImplementation(() => {
    if (process.env.PALO_ALTO_API_KEY && process.env.PALO_ALTO_API_URL) {
      return true;
    }
    return false;
  }),
}));

// Mock the PanOsSdkClient class
vi.mock('../src/utils/pan-os-sdk-client', () => ({
  PanOsSdkClient: vi.fn().mockImplementation(() => ({
    getAddressObjects: vi.fn().mockResolvedValue([
      { name: 'test-address', type: 'ip-netmask', value: '192.168.1.1/24' }
    ]),
    getSecurityZones: vi.fn().mockResolvedValue([
      { name: 'trust', mode: 'layer3' }
    ]),
    getSecurityPolicies: vi.fn().mockResolvedValue([
      { 
        name: 'allow-out', 
        fromZones: ['trust'], 
        toZones: ['untrust'],
        sourceAddresses: ['any'],
        destinationAddresses: ['any'],
        applications: ['web-browsing'],
        services: ['application-default'],
        action: 'allow'
      }
    ]),
  })),
}));

// Import main after setting up mocks
import { main } from '../src/main';
import { validateConfig } from '../src/utils/helpers';

describe('Palo Alto MCP Server', () => {
  it('should successfully start when configuration is valid', async () => {
    // Make sure validateConfig returns true
    vi.mocked(validateConfig).mockReturnValue(true);
    
    await main();
    
    // Process.exit should not be called on success
    expect(process.exit).not.toHaveBeenCalled();
    
    // Verify McpServer was initialized correctly
    expect(McpServer).toHaveBeenCalledWith({
      name: 'palo-alto-mcp',
      version: '0.1.0',
    });
    
    // Verify StdioServerTransport was created
    expect(StdioServerTransport).toHaveBeenCalled();
  });
  
  it('should exit with error when API key is missing', async () => {
    // Simulate missing API key
    delete process.env.PALO_ALTO_API_KEY;
    vi.mocked(validateConfig).mockReturnValue(false);
    
    await main();
    
    // Verify process.exit was called with error code
    expect(process.exit).toHaveBeenCalledWith(1);
  });
  
  it('should exit with error when API URL is missing', async () => {
    // Simulate missing API URL
    delete process.env.PALO_ALTO_API_URL;
    vi.mocked(validateConfig).mockReturnValue(false);
    
    await main();
    
    // Verify process.exit was called with error code
    expect(process.exit).toHaveBeenCalledWith(1);
  });
});
