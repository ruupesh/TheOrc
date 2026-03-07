# Time & Timezone Assistant Agent

A specialized time and timezone agent that provides current times, converts between timezones, helps schedule meetings, and performs date/time calculations.

## MCP Server

Uses `mcp-server-time` (uvx/pip) — the official Time MCP server.

### Tools Provided
- `get_current_time` — Get the current time in a specified timezone
- `convert_time` — Convert a time between timezones

## Setup

1. Copy `.env.sample` to `.env` and fill in values.
2. No additional authentication required.
3. Install: `pip install mcp-server-time`

## Running

```bash
uvicorn app.agentic.time_assistant.agent:a2a_app --host 0.0.0.0 --port 8010
```

## Port: 8010
