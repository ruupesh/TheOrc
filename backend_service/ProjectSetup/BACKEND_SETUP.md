# Backend Setup

This guide covers local setup for the FastAPI backend and the remote agent services used by TheOrchestrator.

## 1. Prerequisites

Install the following first:

- Python 3.11 or newer
- PostgreSQL running locally or in Docker
- Windows PowerShell
- Windows Terminal (`wt.exe`) if you want to launch all agents with the provided script

Database setup is documented in [POSTGRES_SETUP.md](d:/projects/TheOrchestrator/backend_service/ProjectSetup/POSTGRES_SETUP.md).

## 2. Create and Activate a Virtual Environment

From [backend_service](d:/projects/TheOrchestrator/backend_service):

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure Environment Variables

Create a `.env` file in [backend_service](d:/projects/TheOrchestrator/backend_service).

Minimum variables:

```env
GOOGLE_API_KEY=your_google_api_key
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/my_db
SECRET_KEY=replace-with-a-strong-secret
```

Common optional variables:

```env
AGENT_MODEL=gemini/gemini-3.1-flash-preview
AGENT_REASONING_EFFORT=medium
AGENT_THINKING_LEVEL=medium
AGENT_INCLUDE_THOUGHTS=false
DDG_MCP_PATH=<path to duckduckgo_mcp_server/server.py>
ORCHESTRATOR_ENABLE_DIRECT_MCP_TOOLS=false
A2A_AUTH_REQUIRED=false
```

Notes:

- `DATABASE_URL` must point to the same PostgreSQL instance you created in the Postgres guide.
- `SECRET_KEY` is used by the auth system for JWT signing.
- `A2A_AUTH_REQUIRED=false` keeps remote A2A agent endpoints open for local development.
- `NEXT_PUBLIC_API_URL` belongs in the frontend, not the backend.

## 4. Bootstrap the Database

Run the initialization script once after the database is available:

```powershell
alembic upgrade head
python -m scripts.init_db
```

What this does:

- Creates database tables
- Applies schema migrations
- Creates the system user
- Seeds system agents from `app/agentic/adapters/remote_agents_conf.yml`
- Seeds system MCP tools from `app/agentic/adapters/mcp_conf.yml`

Optional marketplace sample data:

```powershell
python -m scripts.migrate_and_seed_marketplace
python -m scripts.seed_agent_listings
```

Use these only if you want sample marketplace listings for demo or UI testing.

## 5. Start the Main API Only

From [backend_service](d:/projects/TheOrchestrator/backend_service):

```powershell
.\venv\Scripts\Activate.ps1
python run.py
```

The API starts on:

```text
http://127.0.0.1:8000
```

Swagger/OpenAPI docs are available at:

```text
http://127.0.0.1:8000/docs
```

## 6. Start the Full Multi-Agent Stack

The orchestrator can call remote agents running on ports `8001` through `8011`.

To launch the main API plus all remote agents in separate Windows Terminal tabs:

```powershell
.\start_all_agents.ps1
```

This starts:

- API server on `8000`
- Job Search on `8001`
- GitHub Assistant on `8002`
- Filesystem Assistant on `8003`
- Web Research Assistant on `8004`
- Knowledge Manager on `8005`
- Database Analyst on `8006`
- Reasoning Assistant on `8007`
- Browser Automation on `8008`
- Git Assistant on `8009`
- Time Assistant on `8010`
- Report Writer on `8011`

If you do not have Windows Terminal, start services manually with `uvicorn`.

Example:

```powershell
uvicorn app.main:app --host localhost --port 8000 --reload
uvicorn app.agentic.web_research_assistant.agent:a2a_app --host localhost --port 8004
```

## 7. Verify the Backend

Quick checks:

1. Open `http://127.0.0.1:8000/docs`.
2. Register a user and log in.
3. Import [TheOrchestrator.postman_collection.json](d:/projects/TheOrchestrator/backend_service/TheOrchestrator.postman_collection.json) into Postman if you want a ready-made API collection.
4. Open the frontend after it is configured and verify login, marketplace, and chat.

## 8. Troubleshooting

### Database connection errors

- Confirm PostgreSQL is running.
- Confirm `DATABASE_URL` matches your container or local server credentials.
- Confirm the target database already exists.

### `ModuleNotFoundError` or import errors

- Make sure the virtual environment is activated.
- Re-run `pip install -r requirements.txt`.
- Start commands from [backend_service](d:/projects/TheOrchestrator/backend_service), not from another directory.

### Remote agent `401 Unauthorized`

- For local development, keep `A2A_AUTH_REQUIRED=false`.
- Restart the agent processes after changing auth-related environment variables or shared agent code.

### Backend runs but chat cannot use sub-agents

- Make sure the remote agents are running on ports `8001` to `8011`.
- Make sure `scripts.init_db` has been run at least once.
- Check each service tab for startup errors.