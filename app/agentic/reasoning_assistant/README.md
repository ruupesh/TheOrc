# Reasoning Assistant Agent

A specialized reasoning and problem-solving agent that uses structured sequential thinking to break down complex problems, analyze decisions, and plan tasks.

## MCP Server

Uses `@modelcontextprotocol/server-sequential-thinking` (npx) — the official Sequential Thinking MCP server.

### Tools Provided
- `sequentialthinking` — A tool for dynamic, reflective problem-solving through structured sequential thinking steps. Supports branching, revision, and hypothesis tracking.

## Setup

1. Copy `.env.sample` to `.env` and fill in values.
2. No additional authentication required.

## Use Cases
- Complex multi-step problem decomposition
- Decision analysis with pros/cons evaluation
- Debugging through systematic elimination
- Project planning with dependency mapping
- Mathematical and logical reasoning

## Running

```bash
uvicorn app.agentic.reasoning_assistant.agent:a2a_app --host 0.0.0.0 --port 8007
```

## Port: 8007
