#!/bin/bash

# Get the absolute path of the script's directory
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Change to the script's directory
cd "$SCRIPT_DIR"

# Run the server, redirecting all output to a log file
python3 mcp_server.py --transport stdio >> mcp_server.log 2>&1
