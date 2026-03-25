# Demo DB Seed Runbook

This runbook prepares a **clean local demo database** with:
- 3 users (`user1`, `user2`, `user3`)
- 11 agents distributed as `4 / 3 / 4`
- 10 MCP tools distributed as evenly as possible (`4 / 3 / 3`)
- all seeded agents and MCP tools published in marketplace

## Prerequisites

- PostgreSQL is running and reachable by `DATABASE_URL` in `backend_service/.env`.
- Python virtual environment exists at `backend_service/venv`.
- You are running commands from `backend_service` folder.

## What each script does

1. `scripts/seed_users.py.py`
   - Creates tables if missing.
   - **Clears all existing rows** (destructive, for local demo use).
   - Creates exactly 3 users:
     - `user1@example.com` / `user1234`
     - `user2@example.com` / `user1234`
     - `user3@example.com` / `user1234`

2. `scripts/seed_agents_and_market.py`
   - Reads all agent configs from `app/agentic/adapters/remote_agents_conf.yml`.
   - Seeds 11 agents with ownership by port:
     - user1: `8001-8004`
     - user2: `8005-8007`
     - user3: `8008-8011`
   - Publishes all seeded agents to marketplace.

3. `scripts/seed_mcp_and_market.py`
   - Reads MCP configs from `app/agentic/adapters/mcp_conf.yml`.
   - Seeds all MCP tools and distributes ownership equally as possible across user1/user2/user3.
   - Publishes all seeded MCP tools to marketplace.

## Run Order (manual)

Run these scripts **in order**:

```bash
python -m scripts.seed_users
python -m scripts.seed_agents_and_market
python -m scripts.seed_mcp_and_market
```

## Quick verification

After running all scripts and starting backend:

- Login as each seeded user and verify pages:
  - `/agents`
  - `/mcp-tools`
  - `/marketplace`

Expected:
- `/marketplace` contains both agent and MCP listings.
- user1 owns first 4 agents by port, user2 next 3, user3 last 4.
- MCP tools are split near-evenly across users.

## Notes for teammates

- Script 1 is intentionally destructive and should only be used for local demo databases.
- Passwords are hashed in DB; plain password for all 3 demo users is `user1234`.
- If you need to re-seed, just run all 3 scripts again in the same order.
