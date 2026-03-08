# Git Assistant Agent

A specialized Git operations agent that analyzes commit history, shows diffs, manages branches, and investigates code changes.

## MCP Server

Uses `mcp-server-git` (uvx/pip) — the official Git MCP server.

### Tools Provided
- `git_log` — Show commit history with filtering options
- `git_diff` — Show diffs between commits, branches, or working tree
- `git_status` — Show working tree status
- `git_show` — Show details of a specific commit
- `git_diff_staged` — Show staged changes
- `git_diff_unstaged` — Show unstaged changes
- `git_list_branches` — List all branches

## Setup

1. Copy `.env.sample` to `.env` and fill in values.
2. Set `GIT_REPO_PATH` to the path of the Git repository to analyze.
3. Install: `pip install mcp-server-git`

## Running

```bash
uvicorn app.agentic.git_assistant.agent:a2a_app --host 0.0.0.0 --port 8009
```

## Port: 8009
