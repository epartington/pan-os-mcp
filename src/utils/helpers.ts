import { v4 as uuidv4 } from 'uuid';

// Config object to store environment variables
export const config = {
  apiKey: process.env.PALO_ALTO_API_KEY || '',
  apiUrl: process.env.PALO_ALTO_API_URL || '',
  debug: process.env.DEBUG === 'true',
};

// Generate a unique request ID for logging
export function generateRequestId(): string {
  return uuidv4();
}

// Structured logging with request ID
export function log(message: string, data?: any, requestId?: string): void {
  const logEntry = {
    timestamp: new Date().toISOString(),
    request_id: requestId || 'server',
    message,
    ...(data ? { data } : {}),
  };

  if (config.debug) {
    console.error(JSON.stringify(logEntry));
  }
}

// Validate required environment variables
export function validateConfig(): boolean {
  const missingVars = [];

  if (!config.apiKey) missingVars.push('PALO_ALTO_API_KEY');
  if (!config.apiUrl) missingVars.push('PALO_ALTO_API_URL');

  if (missingVars.length > 0) {
    log(`Missing required environment variables: ${missingVars.join(', ')}`);
    return false;
  }

  return true;
}
