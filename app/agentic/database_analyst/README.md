# Database Analyst Agent

A specialized database analyst agent that executes SQL queries, designs schemas, analyzes data, and manages SQLite databases.

## MCP Server

Uses `mcp-server-sqlite` (uvx/pip) — the official SQLite MCP server.

### Tools Provided
- `read_query` — Execute a SELECT query and return results
- `write_query` — Execute INSERT, UPDATE, or DELETE queries
- `create_table` — Create a new table with specified schema
- `list_tables` — List all tables in the database
- `describe_table` — Get column info for a specific table
- `append_insight` — Store an analytical insight

## Setup

1. Copy `.env.sample` to `.env` and fill in values.
2. Set `SQLITE_DB_PATH` to the path of your SQLite database file.
3. Install: `pip install mcp-server-sqlite`

## Running

```bash
uvicorn app.agentic.database_analyst.agent:a2a_app --host 0.0.0.0 --port 8006
```

## Port: 8006
