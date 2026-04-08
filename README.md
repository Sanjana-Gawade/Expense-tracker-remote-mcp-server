Setup & Running
Prerequisites

Python 3.12
Node.js (for MCP Inspector)
uv package manager

Installation
1. Clone the repository and navigate to the project:
cd test_remote_server

2. Create .python-version file:
New-Item -Path .python-version -ItemType File -Value "3.12"

3. Create virtual environment with Python 3.12:
uv venv --python 3.12
4. Install dependencies:
powershelluv sync

Running the Server
Terminal 1 — Start the MCP server:
powershelluv run python main.py
Server will start at http://localhost:8000

Testing with MCP Inspector
Terminal 2 — Open MCP Inspector:
powershellnpx @modelcontextprotocol/inspector http://localhost:8000/mcp
Then open the URL shown in the terminal in your browser.

Project Structure
test_remote_server/
├── main.py          # MCP server
├── pyproject.toml   # Project dependencies
├── .python-version  # Python version pin (3.12)
└── README.md