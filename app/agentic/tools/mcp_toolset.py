import os
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

from dotenv import load_dotenv
load_dotenv()

DDG_MCP_PATH = os.getenv("DDG_MCP_PATH")

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