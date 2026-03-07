# Report Writer Agent

A specialized report writing agent that researches topics from the web and produces well-structured, professional reports saved to disk.

## MCP Servers

Uses `@modelcontextprotocol/server-fetch` (npx) — the official Fetch MCP server for web research.
Also uses the custom `write_to_disk` tool for saving reports.

### Tools Provided
- `fetch` — Fetch a URL and return the content as markdown
- `write_to_disk` — Save the generated report to a file on disk

## Setup

1. Copy `.env.sample` to `.env` and fill in values.
2. No additional authentication required.

## Output Format

Reports are saved as Markdown files with the naming convention:
`report_<topic>_YYYY-MM-DD.md`

## Running

```bash
uvicorn app.agentic.report_writer.agent:a2a_app --host 0.0.0.0 --port 8011
```

## Port: 8011
