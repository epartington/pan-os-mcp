import { log } from './utils/helpers';
import fs from 'fs';
import path from 'path';
import os from 'os';

/**
 * Initialize the configuration settings for the MCP server.
 * This creates or updates a configuration file in the user's home directory.
 */
export function init(): void {
  log('Initializing Palo Alto MCP server configuration...');

  try {
    // Create a sample configuration file or update an existing one
    const configDir = path.join(os.homedir(), '.palo-alto-mcp');
    const configFile = path.join(configDir, 'config.json');

    // Create directory if it doesn't exist
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
      log(`Created configuration directory: ${configDir}`);
    }

    // Default configuration
    const defaultConfig = {
      apiKey: process.env.PALO_ALTO_API_KEY || '[YOUR_API_KEY]',
      apiUrl: process.env.PALO_ALTO_API_URL || 'https://[FIREWALL_IP_OR_HOSTNAME]/api',
      debug: process.env.DEBUG === 'true',
    };

    // Write or update configuration file
    if (!fs.existsSync(configFile)) {
      fs.writeFileSync(configFile, JSON.stringify(defaultConfig, null, 2));
      log(`Created new configuration file: ${configFile}`);
    } else {
      // Read existing config and merge with defaults
      const existingConfig = JSON.parse(fs.readFileSync(configFile, 'utf8'));
      const mergedConfig = { ...defaultConfig, ...existingConfig };
      fs.writeFileSync(configFile, JSON.stringify(mergedConfig, null, 2));
      log(`Updated existing configuration file: ${configFile}`);
    }

    // Completion message with instructions
    log(`
==========================================================
Palo Alto MCP Server Initialization Complete
==========================================================

Configuration file created at: ${configFile}

To use this MCP server with Windsurf, please follow these steps:

1. Edit the configuration file to include your API key and firewall URL:
   ${configFile}

2. Add this MCP server to your Windsurf config:
   {
     "command": "npx -y palo-alto-mcp",
     "args": []
   }

3. Set environment variables for API credentials:
   export PALO_ALTO_API_KEY="your-api-key"
   export PALO_ALTO_API_URL="https://your-firewall-ip/api"

For more information, please refer to the README.md file.
==========================================================
`);
  } catch (error) {
    log('Error during initialization:', error);
    log('Failed to initialize the Palo Alto MCP server configuration.');
    process.exit(1);
  }
}
