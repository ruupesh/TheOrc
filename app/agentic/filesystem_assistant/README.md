# Filesystem Assistant Agent

A specialized filesystem operations agent that explores, reads, writes, searches, and manages files and directories.

## MCP Server

Uses `@modelcontextprotocol/server-filesystem` (npx) — the official Filesystem MCP server.

### Tools Provided
- `read_file` — Read contents of a file
- `write_file` — Write content to a file
- `list_directory` — List directory contents
- `create_directory` — Create a new directory
- `move_file` — Move or rename files
- `search_files` — Search for files by pattern
- `get_file_info` — Get file metadata (size, timestamps)
- `read_multiple_files` — Read multiple files at once

## Setup

1. Copy `.env.sample` to `.env` and fill in values.
2. Set `FILESYSTEM_ALLOWED_PATHS` to comma-separated list of directories the agent can access.

## Security

The filesystem server only allows access to explicitly configured paths. It will refuse operations outside these directories.

## Running

```bash
uvicorn app.agentic.filesystem_assistant.agent:a2a_app --host 0.0.0.0 --port 8003
```

## Port: 8003
