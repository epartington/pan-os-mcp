import { v4 as uuidv4 } from 'uuid';

// Config object to store environment variables
export const config = {
  apiKey: process.env.PALO_ALTO_API_KEY || '',
  apiUrl: process.env.PALO_ALTO_API_URL || '',
  debug: process.env.DEBUG === 'true',
  devMode: process.env.DEV_MODE === 'true',
};

// Generate a unique request ID for logging
export function generateRequestId(): string {
  return uuidv4();
}

// Structured logging with request ID
export function log(message: string, data?: unknown, requestId?: string): void {
  const logEntry = {
    timestamp: new Date().toISOString(),
    request_id: requestId || 'server',
    message,
    ...(data ? { data } : {}),
  };

  // Output log entry to stderr (this is expected behavior for this app)
  process.stderr.write(JSON.stringify(logEntry) + '\n');
}

// Validate required environment variables
export function validateConfig(): boolean {
  // If in dev mode, don't require API credentials
  if (config.devMode) {
    log('Running in development mode - API credentials not required');
    return true;
  }

  const missingVars = [];

  if (!process.env.PALO_ALTO_API_KEY) {
    missingVars.push('PALO_ALTO_API_KEY');
  }

  if (!process.env.PALO_ALTO_API_URL) {
    missingVars.push('PALO_ALTO_API_URL');
  }

  if (missingVars.length > 0) {
    log('Missing required environment variables: ' + missingVars.join(', '));
    return false;
  }

  return true;
}
