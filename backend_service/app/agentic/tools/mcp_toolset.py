import os
from pathlib import Path
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV_PATH)

DDG_MCP_PATH = os.getenv("DDG_MCP_PATH")

# ---------------------------------------------------------------------------
# DuckDuckGo Search (used by job_search agent)
# ---------------------------------------------------------------------------
duckduckgo_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=[
                "run",
                DDG_MCP_PATH,
            ],
        ),
        timeout=30.0,
    )
)

# ---------------------------------------------------------------------------
# GitHub MCP — repo management, issues, PRs, code search
# Requires GITHUB_PERSONAL_ACCESS_TOKEN env var
# ---------------------------------------------------------------------------
github_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={
                **os.environ,
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv(
                    "GITHUB_PERSONAL_ACCESS_TOKEN", ""
                ),
            },
        ),
        timeout=30.0,
    )
)

# ---------------------------------------------------------------------------
# Filesystem MCP — read, write, search, list files within allowed paths
# Set FILESYSTEM_ALLOWED_PATHS env var (comma-separated) to restrict access
# ---------------------------------------------------------------------------
_fs_paths = os.getenv("FILESYSTEM_ALLOWED_PATHS", os.getcwd()).split(",")
filesystem_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem"]
            + [p.strip() for p in _fs_paths],
        ),
        timeout=30.0,
    )
)

# ---------------------------------------------------------------------------
# Fetch MCP — fetch web pages and extract content as markdown
# No authentication required
# ---------------------------------------------------------------------------
fetch_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "fetch-mcp"],
        ),
        timeout=30.0,
    )
)

# ---------------------------------------------------------------------------
# Memory MCP — persistent knowledge graph with entities and relations
# No authentication required
# ---------------------------------------------------------------------------
memory_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-memory"],
            env={
                "MEMORY_FILE_PATH": "D:/projects/TheOrchestrator/backend_service/conversation_logs/memory.jsonl",
            },
        ),
        timeout=300.0,
    )
)

# ---------------------------------------------------------------------------
# SQLite MCP — query, analyze, and manage SQLite databases
# Set SQLITE_DB_PATH env var to point to the database file
# ---------------------------------------------------------------------------
sqlite_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uvx",
            args=[
                "mcp-server-sqlite",
                "--db-path",
                os.getenv("SQLITE_DB_PATH", "database.db"),
            ],
        ),
        timeout=30.0,
    )
)

# ---------------------------------------------------------------------------
# Sequential Thinking MCP — structured multi-step reasoning
# No authentication required
# ---------------------------------------------------------------------------
sequential_thinking_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-sequential-thinking"],
        ),
        timeout=30.0,
    )
)

# ---------------------------------------------------------------------------
# Puppeteer MCP — browser automation, screenshots, web scraping
# No authentication required (needs Chrome/Chromium installed)
# ---------------------------------------------------------------------------
puppeteer_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-puppeteer"],
        ),
        timeout=30.0,
    )
)

# ---------------------------------------------------------------------------
# Git MCP — git log, diff, blame, branch listing, file history
# Set GIT_REPO_PATH env var to the target repository path
# ---------------------------------------------------------------------------
git_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uvx",
            args=[
                "mcp-server-git",
                "--repository",
                os.getenv("GIT_REPO_PATH", "."),
            ],
        ),
        timeout=30.0,
    )
)

# ---------------------------------------------------------------------------
# Time MCP — current time, timezone conversions, date calculations
# No authentication required
# ---------------------------------------------------------------------------
time_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uvx",
            args=["mcp-server-time"],
        ),
        timeout=30.0,
    )
)
