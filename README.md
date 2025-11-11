# Claude MT5 MCP Server Linux-Specific

## ***COMPLETION PENDING***

> A local MCP server for Claude Desktop to interact with the MetaTrader 5 terminal running on Linux via Wine.

This project bridges the gap between the native Linux Claude Desktop application and the Windows-only MetaTrader 5 terminal. It allows Claude to access account information, pull market data, and analyze indicators directly from your trading platform.

---

## ⚠️ Security & Architecture Warning

This is not a standard, enterprise-grade solution. It is a **clever, expert-level workaround** that depends on a complex and brittle chain of technologies:

1.  **Wine:** We run the Windows MT5 terminal on Linux using the Wine compatibility layer.
2.  **Wine-Python:** We install a *second*, Windows-native Python interpreter *inside* Wine.
3.  **GUI-Dependent:** This server **requires** the MetaTrader 5 desktop application to be open, running, and logged in. It is not a headless, 24/7 server.

This setup can be fragile. A simple update to Wine, MT5, or your Linux drivers could break it. **Always test on a demo account first.** Use at your own risk.

---

## ⚙️ How It Works

1.  **Claude Desktop** starts your `run.sh` script, which is registered in its config.
2.  The `run.sh` script launches `wine python.exe` (the Windows Python in Wine).
3.  This Wine-Python script (`mcp_server.py`) starts and listens for commands on `stdio`.
4.  When Claude sends a request (e.g., "get balance"), the script imports the `MetaTrader5` library.
5.  It then connects to your *running* `mt5.exe` application, fetches the data, and sends it back to Claude as JSON.

---

## 🚀 Installation and Setup Guide

This is a complete, step-by-step guide from a fresh Linux Mint / Ubuntu-based system.

### Step 1: Install Core Linux Dependencies (Git & Wine)

First, we need the `git` client to download the project and the `wine` compatibility layer to run Windows apps.

```bash
# Update your package lists
sudo apt update

# Install git
sudo apt install git -y

# Install Wine (this is the main, stable package)
sudo apt install wine -y
````

### Step 2: Get the Project Code

Clone this repository to your home directory.

```bash
# Navigate to your home directory
cd ~

# Clone the project
git clone [https://github.com/CrysiscodeX/claude-mt5-mcp.git](https://github.com/CrysiscodeX/claude-mt5-mcp.git)

# Enter the new project directory
cd claude-mt5-mcp
```

### Step 3: Install MetaTrader 5 (via Wine)

This uses the official Linux installation script, which installs the Windows version using Wine.

```bash
# Download the official MT5 Linux installer
wget [https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5linux.sh](https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5linux.sh)

# Make the script executable
chmod +x mt5linux.sh

# Run the installer. This will open a standard Windows-style setup wizard.
./mt5linux.sh
```

**Follow the on-screen installer** just as you would on Windows.

### Step 4: Install Windows Python (via Wine)

Now, we must install a Windows-native Python *inside* our Wine environment.

```bash
# Download the Windows Python 3.11 installer
wget [https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe](https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe)

# Run the installer using Wine
wine python-3.11.5-amd64.exe
```

A Windows installer will pop up. **This is the most important step:**

1.  **CHECK** the box at the bottom that says **"Add python.exe to PATH"**.
2.  Click **"Install Now"**.

### Step 5: Install Python Dependencies (via Wine-Pip)

With our Wine-Python installed, we now use its `pip` to install the required Windows libraries.

```bash
# 1. Update Wine-Pip to the latest version
wine python.exe -m pip install --upgrade pip

# 2. Install the MetaTrader5 library (Windows version)
wine pip install MetaTrader5

# 3. Install the jsonschema library (Windows version)
wine pip install jsonschema
```

-----

## 🛠️ Configuration

Your code is now 100% installed. We just need to configure the applications to talk to each other.

### Part 1: Configure MetaTrader 5

1.  Open the **MetaTrader 5** application you installed.
2.  In the top menu, go to **Tools** -\> **Options**.
3.  Click the **Expert Advisors** tab.
4.  **CHECK** the box for **"Allow Algo Trading"**.
5.  Click **OK**.

### Part 2: Configure Claude Desktop

This is the final step. We need to manually edit Claude's config file to tell it about our new server.

**1. Get Your Project's Absolute Path**

Run this command while in your project folder to get the exact path:

```bash
pwd
```

It will output something like: `/home/codexwz01d/claude-mt5-mcp`. Copy this path.

**2. Edit the Claude Config File**

Open the Claude config file with your text editor. The file is located at:
`/home/codexwz01d/.config/Claude/claude_desktop_config.json`

**BEFORE YOU EDIT,** your file might look like this (or be empty):

```json
{
  "mcpServers": {
    "some-other-server": {
      "command": "npx",
      "args": [ ... ]
    }
  }
}
```

**AFTER EDITING,** add your new server. **Do not remove existing servers.** Paste your absolute path into the `command` field.

```json
{
  "mcpServers": {
    "some-other-server": {
      "command": "npx",
      "args": [ ... ]
    },
    "mt5-local-server": {
      "command": "/home/user_name/claude-mt5-mcp/run.sh",
      "args": []
    }
  }
}
```

**Save the file.**

-----

## ⚡ Running the Server

You are ready\!

1.  **Fully RESTART your Claude Desktop** application (quit and re-open it).
2.  **Make sure your MetaTrader 5** application is **open, running, and logged in** to your trading account.
3.  In Claude, open **Settings** -\> **Developer** -\> **Extensions**.
4.  You should see `mt5-local-server` listed with a **"running"** status.
5.  Open a new chat and test it\!

#### Example Prompts:

  * *"Using my MT5 tools, what is my account balance?"*
  * *"What is the current bid/ask spread for EURUSD?"*
  * *"Get the last 10 hourly bars for GBPUSD."*
  * *"What is the 14-period SMA for EURUSD on the H1 timeframe?"*

-----

## 🔍 Troubleshooting

  * **"Server disconnected" or "failed" status in Claude:**

    1.  **Is MT5 running?** This is the \#1 cause. The server *will not start* if it can't connect to MT5.
    2.  **Is "Allow Algo Trading" checked?**
    3.  **Check the log file:** The script redirects all errors to `mcp_server.log` in your project folder. Open this file to see the exact Python error.

  * **GitHub Actions CI is Failing (Red X):**
    This is **expected**. The GitHub Actions runner is a clean Linux machine. It does not have Wine or a Windows Python environment, so the `test_mt5_tools.py` script fails when it tries to `import MetaTrader5`. This does not affect your local setup.

<!-- end of list ... kinda -->
