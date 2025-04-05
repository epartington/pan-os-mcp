# Palo Alto MCP Server Troubleshooting Guide

This document provides solutions for common issues you might encounter when using the Palo Alto MCP server, including installation problems, configuration issues, and API connectivity challenges.

## Installation Issues

### npm Install Failures

**Problem**: `npm install -g palo-alto-mcp` fails with permission errors.

**Solution**:
```bash
# Option 1: Use sudo (not recommended for security reasons)
sudo npm install -g palo-alto-mcp

# Option 2: Fix npm permissions (recommended)
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.profile
source ~/.profile
npm install -g palo-alto-mcp
```

**Problem**: Package installation fails with dependency conflicts.

**Solution**:
```bash
# Clear npm cache and try again
npm cache clean --force
npm install -g palo-alto-mcp

# Alternative: Use npx without installing
npx -y palo-alto-mcp
```

### Node.js Version Issues

**Problem**: Error about incompatible Node.js version.

**Solution**:
```bash
# Check your current Node.js version
node --version

# Install recommended version (18.x or later)
# Using nvm (Node Version Manager):
nvm install 18
nvm use 18
npm install -g palo-alto-mcp
```

## Configuration Issues

### Missing Environment Variables

**Problem**: Server fails with "API key is required" or "API URL is required" errors.

**Solution**:
1. Set the required environment variables:
   ```bash
   export PALO_ALTO_API_KEY="your-api-key-here"
   export PALO_ALTO_API_URL="https://your-firewall-ip-or-hostname/api"
   ```

2. Verify the variables are set correctly:
   ```bash
   echo $PALO_ALTO_API_KEY
   echo $PALO_ALTO_API_URL
   ```

3. For persistent configuration, add to your shell profile:
   ```bash
   echo 'export PALO_ALTO_API_KEY="your-api-key-here"' >> ~/.bashrc
   echo 'export PALO_ALTO_API_URL="https://your-firewall-ip-or-hostname/api"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Client Configuration Problems

**Problem**: Windsurf client can't find or start the Palo Alto MCP server.

**Solution**:
1. Check your `mcp_config.json` configuration:
   ```json
   {
     "palo-alto": {
       "command": "npx -y palo-alto-mcp",
       "args": []
     }
   }
   ```

2. Verify the server is executable via CLI:
   ```bash
   npx -y palo-alto-mcp
   ```

3. Ensure environment variables are set in the same context where Windsurf runs.

## API Connectivity Issues

### Authentication Failures

**Problem**: "API key authentication failed" error when making requests.

**Solution**:
1. Verify your API key is correct and has not expired.
2. Check that the API key has sufficient permissions on the firewall.
3. Test the API key directly with curl:
   ```bash
   curl -k "https://your-firewall-ip/api/?type=keygen&key=your-api-key"
   ```

### Network Connectivity Issues

**Problem**: "Unable to connect to firewall" or timeout errors.

**Solution**:
1. Verify network connectivity to the firewall:
   ```bash
   ping your-firewall-ip
   ```

2. Check if the firewall's management interface is accessible:
   ```bash
   telnet your-firewall-ip 443
   ```

3. Verify no firewalls or proxies are blocking the connection.

4. Ensure the HTTPS URL is correctly formatted:
   ```
   # Correct format
   https://10.0.0.1/api
   
   # Incorrect formats
   https://10.0.0.1:443/api  # Don't specify default port 443
   https://10.0.0.1api       # Missing slash before 'api'
   http://10.0.0.1/api       # Using HTTP instead of HTTPS
   ```

### SSL/TLS Certificate Issues

**Problem**: SSL certificate verification errors.

**Solution**:
1. If using a self-signed certificate on the firewall, you may need to set an environment variable to disable certificate verification (not recommended for production):
   ```bash
   # Note: This is a security risk but may be needed for testing
   export NODE_TLS_REJECT_UNAUTHORIZED=0
   ```

2. Better solution: Import the firewall's certificate into your system's trusted certificate store.

## Tool Execution Issues

### Invalid Parameters

**Problem**: "Invalid params" errors when calling tools.

**Solution**:
1. Check the required parameters for each tool:
   - `retrieve_address_objects`: Requires `location` parameter
   - `retrieve_security_zones`: Requires `location` parameter
   - `retrieve_security_policies`: Requires `location` parameter

2. Verify parameter types (all should be strings).

3. Debug the exact request:
   ```bash
   DEBUG=true npx -y palo-alto-mcp
   ```

### Empty Results

**Problem**: Tools execute successfully but return empty arrays.

**Solution**:
1. Verify the firewall has the objects you're looking for.
2. Check if the vsys parameter is correct (default is "vsys1").
3. Ensure the API key has permissions to view the requested configuration.
4. Try running a direct API query to verify data exists:
   ```bash
   curl -k "https://your-firewall-ip/api/?type=config&action=get&xpath=/config/devices/entry/vsys/entry[@name='vsys1']/address&key=your-api-key"
   ```

## Performance Issues

### Slow Response Times

**Problem**: Tool calls take a long time to complete.

**Solution**:
1. Check network latency to the firewall:
   ```bash
   ping your-firewall-ip
   ```

2. Verify the firewall is not under heavy load.

3. For large configurations, consider implementing pagination or filtering (future enhancement).

### High CPU or Memory Usage

**Problem**: The server consumes excessive system resources.

**Solution**:
1. Check if processing large response datasets; consider filtering at the API level.
2. Ensure you're not creating multiple server instances.
3. Update to the latest version which may contain performance improvements.

## Logging and Debugging

### Enabling Debug Mode

To get detailed logs for troubleshooting:

```bash
# Enable debug logging
export DEBUG=true
npx -y palo-alto-mcp
```

### Log File Capture

Capture logs to a file for detailed analysis:

```bash
DEBUG=true npx -y palo-alto-mcp 2> palo-alto-mcp.log
```

### Analyzing Requests and Responses

To see the exact API requests and responses:

```bash
# Make a direct API call with curl for comparison
curl -k "https://your-firewall-ip/api/?type=config&action=get&xpath=/config/devices/entry/vsys/entry[@name='vsys1']/address&key=your-api-key"

# Compare with debug logs from the MCP server
```

## Common Error Messages and Resolutions

### "Unknown tool: [tool_name]"

**Cause**: The requested tool doesn't exist or is misspelled.

**Resolution**: Check available tools with a `list_tools` request. Verify the tool name is exactly as listed.

### "PAN-OS API error: API key authentication failed"

**Cause**: Invalid API key or the key doesn't have permissions.

**Resolution**: Verify the API key and its permissions on the firewall.

### "Failed to connect to firewall: ETIMEDOUT"

**Cause**: Network connectivity issue or firewall is not reachable.

**Resolution**: Check network connectivity, firewall configuration, and ensure the API URL is correct.

### "vsys1 not found"

**Cause**: The specified vsys doesn't exist on the firewall.

**Resolution**: Verify the correct vsys name (usually "vsys1" for single-vsys firewalls).

### "Invalid XML response"

**Cause**: The firewall returned malformed XML or an unexpected response.

**Resolution**: Check the firewall API documentation, ensure the XML API is enabled, and review firewall logs.

## Version-Specific Issues

### Version 0.1.x

Known issues in the initial release:
- Limited error handling for specific PAN-OS error codes
- No support for pagination of large result sets
- Basic authentication only (API key)

Resolutions:
- Use specific error handling where available
- For large configurations, use vsys or other filtering
- Upgrade to newer versions when available

## Getting Further Help

If you continue experiencing issues after trying these troubleshooting steps:

1. Check the GitHub repository for open and closed issues
2. Review the Palo Alto Networks API documentation
3. Capture detailed logs and provide them when seeking help
4. Include your environment details:
   - Operating system
   - Node.js version (`node --version`)
   - npm version (`npm --version`)
   - Palo Alto MCP server version
   - PAN-OS version on the firewall
