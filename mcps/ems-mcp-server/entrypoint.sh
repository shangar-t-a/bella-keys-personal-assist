#!/bin/sh
set -e

echo "Starting EMS MCP Server..."

# Start the application
echo "Starting FastMCP application..."
exec python app/main.py
