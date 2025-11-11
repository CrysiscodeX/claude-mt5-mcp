import sys
import json
import socket
import argparse
import logging
from jsonschema import validate, ValidationError

# Import all tool functions from mt5_tools.py
from mt5_tools import *

# Set up logging
logging.basicConfig(filename='mcp_server_debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Map tool names to their handler functions
TOOL_HANDLERS = {
    'get_account_info': get_account_info,
    'get_symbol_tick': get_symbol_tick,
    'get_historical_data': get_historical_data,
    'get_indicator_value': get_indicator_value,
}

def load_schemas(filename="schemas.json"):
    """Loads tool schemas from a JSON file and keys them by tool name."""
    try:
        with open(filename, 'r') as f:
            schemas_list = json.load(f)
        return {schema['name']: schema for schema in schemas_list}
    except FileNotFoundError:
        logging.error("schemas.json not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error("Error decoding schemas.json.")
        sys.exit(1)

def handle_request(request_data: dict, schemas: dict):
    """Handles a single MCP request."""
    request_id = request_data.get('request_id', 'unknown')
    
    try:
        if request_data.get('tool_name') == 'mcp.list_tools':
            return {
                "request_id": request_id,
                "result": list(schemas.values())
            }

        if request_data.get('tool_name') == 'mcp.invoke_tool':
            tool_name_full = request_data['parameters']['tool_name']
            tool_name_short = tool_name_full.split('mt5.')[-1]
            
            handler = TOOL_HANDLERS.get(tool_name_short)
            if not handler:
                raise ValueError(f"Tool '{tool_name_full}' not found.")

            schema = schemas.get(tool_name_full)
            if not schema:
                raise ValueError(f"Schema for tool '{tool_name_full}' not found.")

            tool_params = request_data['parameters']['parameters']
            
            # Validate parameters against the schema
            validate(instance=tool_params, schema=schema['parameters'])
            
            # Call the tool handler
            result = handler(**tool_params)
            
            return {
                "request_id": request_id,
                "result": result
            }
            
        raise ValueError("Invalid tool_name specified.")

    except (ValueError, KeyError, ValidationError, Exception) as e:
        logging.error(f"Error handling request {request_id}: {e}")
        return {
            "request_id": request_id,
            "error": {
                "message": str(e),
                "code": type(e).__name__
            }
        }

def run_stdio_server(schemas: dict):
    """Runs the server over standard input/output."""
    logging.info("Starting server in stdio mode.")
    for line in sys.stdin:
        try:
            request = json.loads(line)
            logging.debug(f"Received request: {request}")
            response = handle_request(request, schemas)
            json.dump(response, sys.stdout)
            sys.stdout.write('\n')
            sys.stdout.flush()
            logging.debug(f"Sent response: {response}")
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from stdin.")
            # Send an error response for malformed JSON
            error_response = {
                "error": {"message": "Invalid JSON format.", "code": "JSONDecodeError"}
            }
            json.dump(error_response, sys.stdout)
            sys.stdout.write('\n')
            sys.stdout.flush()


def run_tcp_server(port: int, schemas: dict):
    """Runs the server over a TCP socket."""
    logging.info(f"Starting server in TCP mode on port {port}.")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                logging.info(f"Connected by {addr}")
                data = conn.recv(4096)
                if not data:
                    continue
                try:
                    request = json.loads(data.decode('utf-8'))
                    logging.debug(f"Received request: {request}")
                    response = handle_request(request, schemas)
                    conn.sendall(json.dumps(response).encode('utf-8'))
                    logging.debug(f"Sent response: {response}")
                except json.JSONDecodeError:
                    logging.error("Failed to decode JSON from TCP stream.")
                    error_response = {
                        "error": {"message": "Invalid JSON format.", "code": "JSONDecodeError"}
                    }
                    conn.sendall(json.dumps(error_response).encode('utf-8'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP Server for MetaTrader 5")
    parser.add_argument('--transport', choices=['stdio', 'tcp'], default='stdio',
                        help="The transport to use ('stdio' or 'tcp').")
    parser.add_argument('--port', type=int, default=8080,
                        help="The port to use for TCP transport.")
    
    args = parser.parse_args()
    
    loaded_schemas = load_schemas()
    
    if args.transport == 'stdio':
        run_stdio_server(loaded_schemas)
    elif args.transport == 'tcp':
        run_tcp_server(args.port, loaded_schemas)
