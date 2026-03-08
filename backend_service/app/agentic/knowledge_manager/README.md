# Knowledge Manager Agent

A specialized knowledge management agent that maintains a persistent knowledge graph with entities, observations, and relations.

## MCP Server

Uses `@modelcontextprotocol/server-memory` (npx) — the official Memory MCP server.

### Tools Provided
- `create_entities` — Create new entities with observations
- `create_relations` — Define relations between entities
- `add_observations` — Add observations to existing entities
- `delete_entities` — Remove entities from the knowledge graph
- `delete_observations` — Remove specific observations
- `delete_relations` — Remove relations between entities
- `read_graph` — Read the entire knowledge graph
- `search_nodes` — Search for entities by name or content
- `open_nodes` — Open specific entities by name

## Setup

1. Copy `.env.sample` to `.env` and fill in values.
2. No additional authentication required.
3. The knowledge graph persists in a local JSON file managed by the MCP server.

## Running

```bash
uvicorn app.agentic.knowledge_manager.agent:a2a_app --host 0.0.0.0 --port 8005
```

## Port: 8005
