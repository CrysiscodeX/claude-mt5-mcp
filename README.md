# Claude MT5 MCP Server

This project provides a local MCP (Multi-Capability Provider) server that acts as a bridge between Claude and the MetaTrader 5 (MT5) trading terminal. It allows Claude to access market data, account information, and potentially execute trades through the MT5 platform.

## Security Warning

This tool can interact with your MetaTrader 5 account. While the initial tools are read-only, adding trading functions is possible. **Always test on a demo account first.** Use at your own risk.

## Prerequisites

- MetaTrader 5 terminal installed on Linux (via Wine/Proton or similar).
- Python 3.11+ installed.
- In your MT5 Terminal, go to `Tools > Options > Expert Advisors` and check the box for `Allow Algo Trading`.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd claude-mt5-mcp
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Running (for Testing)

You can run the server in TCP mode to test it independently from Claude Desktop. This is useful for debugging the tool functions directly.

```bash
python3 mcp_server.py --transport tcp
```
You can then send JSON requests to port 8080 to test the handlers.

## Claude Desktop Installation

1.  **Make the run script executable:**
    ```bash
    chmod +x run.sh
    ```

2.  **IMPORTANT**: Edit `manifest.json` with a text editor. Change the `command` value to the **absolute path** of `run.sh` on your system (e.g., `/home/codexwz01d/claude-mt5-mcp/run.sh`).

3.  In Claude Desktop, go to `Settings > Extensions > Add Local Extension`.

4.  Select the `manifest.json` file from this project directory. The extension should now be installed and running.
