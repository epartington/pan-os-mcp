#!/usr/bin/env node
import { init } from './init';
import { log } from './utils/helpers';
import { main } from './main';

// Handle process events
process.on('uncaughtException', (error) => {
  log('Uncaught exception:', error);
});

process.on('unhandledRejection', (error) => {
  log('Unhandled rejection:', error);
});

// Process command-line arguments
const [cmd, ...args] = process.argv.slice(2);
if (cmd === 'init') {
  // Initialize configuration
  init();
} else {
  // Start the MCP server
  main().catch((error) => {
    log('Fatal error starting server:', error);
    process.exit(1);
  });
}
