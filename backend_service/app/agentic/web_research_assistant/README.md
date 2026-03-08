# Web Research Assistant Agent

A specialized web research agent that fetches, analyzes, and summarizes content from any public web page or API endpoint.

## MCP Server

Uses `@modelcontextprotocol/server-fetch` (npx) — the official Fetch MCP server.

### Tools Provided
- `fetch` — Fetch a URL and return the content as markdown, text, or raw HTML

## Setup

1. Copy `.env.sample` to `.env` and fill in values.
2. No additional authentication required — fetches public web pages.

## Running

```bash
uvicorn app.agentic.web_research_assistant.agent:a2a_app --host 0.0.0.0 --port 8004
```

## Port: 8004
