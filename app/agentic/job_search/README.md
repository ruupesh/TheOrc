# Job Search Assistant Agent

A specialized agent designed to find job opportunities on the web and persist them to disk in CSV format. This agent is built using the Google ADK and exposed as an Agent-to-Agent (A2A) service.

## Features

- **Web Search**: Uses the DuckDuckGo MCP server to find real-time job listings.
- **Data Persistence**: Automatically converts search results into CSV format and saves them to the local file system.
- **A2A Service**: Runs as a `uvicorn` server, allowing it to be called by other agents (like the Orchestrator).

## Prerequisites

Ensure you have the following environment variables set in your `.env` file:

- `AGENT_MODEL`: The LLM model to use (e.g., `gemini/gemini-1.5-flash`).
- `DDG_MCP_PATH`: The local path to your DuckDuckGo MCP server (e.g., `d:/projects/MultiAgent/venv/Lib/site-packages/duckduckgo_mcp_server/server.py`).

## Installation

Make sure you are in the virtual environment and have the dependencies installed:

```powershell
pip install -r src/requirements.txt
```

## How to Run

1. Navigate to the `src` directory:
   ```powershell
   cd \app
   ```

2. Start the agent server:
   ```powershell
   uvicorn agentic.job_search.agent:a2a_app --host localhost --port 8001
   ```

The agent will be available at `http://localhost:8001`. You can view the agent card at `http://localhost:8001/.well-known/agent-card.json`.

## Tool Usage

- **DuckDuckGo MCP**: Used for searching the web.
- **write_to_disk**: A custom tool that takes a filename and content. If the content is a JSON list of job objects, it converts them to CSV.
