# MultiAgentIntegration App

MultiAgentIntegration App is a full-stack AI orchestration platform that turns a single user request into a routed execution plan across specialist agents, MCP toolsets, and user-governed capability catalogs.

- Two-stage runtime: a discovery agent decides how work should be executed, and a separate orchestrator executes that plan.
- Hybrid execution model: one request can use remote A2A agents, direct MCP tools, or both.
- Multi-tenant governance: JWT auth, session ownership enforcement, per-user capability catalogs, and marketplace installs are built into the platform.
- Stateful conversations: Redis-backed ADK sessions preserve routing state, conversation history, HITL checkpoints, and resumability.
- Distribution built in: agents and MCP tools are persisted in PostgreSQL and can be published, installed, and customized through a marketplace workflow.

![MultiAgentIntegration App Architecture](backend_service/documentation/MultiAgentSystem.png)

## AI Runtime Architecture

The core runtime is implemented as a Google ADK `SequentialAgent` with a strict two-step execution model:

1. `tool_agent_discovery`
2. `Orchestrator`

This split matters. The project does not rely on a single prompt trying to both plan and execute. It first makes an explicit routing decision, stores that decision in session state, and only then composes the runtime needed for execution.

### Stage 1: Discovery

The discovery agent receives:

- the user request
- the currently available remote agent catalog
- the currently available MCP tool catalog

It returns structured JSON with:

- `strategy`
- `agents`
- `mcp_tools`
- `reasoning`

That output is stored in `session.state["discovery_result"]` and becomes the contract between planning and execution.

### Stage 2: Orchestration

The `Orchestrator` reads `discovery_result` inside a `before_agent_callback` and dynamically reconfigures itself for the current request:

- one selected remote specialist becomes a `sub_agent` for efficient one-hop delegation
- multiple specialists are mounted as `AgentTool` wrappers so the orchestrator can call them and chain results
- selected MCP toolsets are attached directly as runtime tools
- built-in function tools remain available for utility operations

This means the execution graph is assembled at runtime per request, not hard-coded ahead of time.

### Runtime State and Resumability

The AI runtime is stateful by design:

- `RedisSessionService` backs ADK session persistence
- root callbacks append user and assistant turns into `conversation_history`
- remote A2A agents can receive forwarded conversation history through request metadata
- `ResumabilityConfig(is_resumable=True)` allows interrupted flows to continue in the same session
- HITL approvals are resumed by posting `content.hitl_approval` back to the same `/chat` session

### Request-Scoped Capability Resolution

At chat time, the backend does not rely on a static in-memory registry. It:

- authenticates the user via JWT
- loads that user's agents and MCP tools from PostgreSQL
- includes installed marketplace capabilities where applicable
- applies optional per-chat allowlists from `enabled_agent_ids` and `enabled_mcp_tool_ids`
- converts the resulting rows into adapter configs for the ADK runtime

That keeps orchestration user-scoped, explainable, and compatible with marketplace installs.

## Routing Strategies

The discovery layer currently selects from five concrete execution modes implemented in the orchestrator:

| Strategy | Runtime shape | When it is used |
| --- | --- | --- |
| `single_agent` | One remote specialist mounted as `sub_agent` | A single specialist can own the task end-to-end |
| `multi_agent` | Multiple specialists mounted as `AgentTool` | The orchestrator needs to call several specialists and combine their outputs |
| `mcp_tools_only` | Selected `McpToolset` instances only | Direct tool execution is enough and no specialist agent is necessary |
| `mcp_tools_with_single_agent` | Selected MCP toolsets plus one `sub_agent` | One specialist is needed, but the orchestrator also needs direct tool access |
| `mcp_tools_with_multi_agent` | Selected MCP toolsets plus multiple `AgentTool` wrappers | Hybrid workflows that require both direct tools and several specialists |

## Capability Matrix

The default specialist fleet runs as separate A2A services on ports `8001` through `8011`.

| Agent | Port | Responsibility | Backing substrate |
| --- | ---: | --- | --- |
| `job_search_assistant` | 8001 | Finds job opportunities and exports results | DuckDuckGo Search MCP + `write_to_disk` |
| `github_assistant` | 8002 | Works with repositories, issues, pull requests, and code search | GitHub MCP |
| `filesystem_assistant` | 8003 | Reads, writes, searches, and manages local files | Filesystem MCP |
| `web_research_assistant` | 8004 | Fetches and summarizes public web content | Fetch MCP |
| `knowledge_manager` | 8005 | Maintains a persistent knowledge graph | Memory MCP |
| `database_analyst` | 8006 | Executes SQL queries and analyzes SQLite data | SQLite MCP |
| `reasoning_assistant` | 8007 | Breaks down complex problems and decision paths | Sequential Thinking MCP |
| `browser_automation` | 8008 | Drives browser workflows and page extraction | Puppeteer MCP |
| `git_assistant` | 8009 | Investigates git history, diffs, branches, and blame | Git MCP |
| `time_assistant` | 8010 | Handles time, timezone, and date calculations | Time MCP |
| `report_writer` | 8011 | Produces structured research reports and saves them to disk | Fetch MCP + `write_to_disk` |

The repo also ships with 10 MCP tool definitions in `backend_service/app/agentic/adapters/mcp_conf.yml`:

- `duckduckgo_search`
- `github`
- `filesystem`
- `fetch`
- `memory`
- `sqlite`
- `sequential_thinking`
- `puppeteer`
- `git`
- `time`

At the orchestrator layer, three built-in function tools are always available:

- `check_prime`
- `check_weather`
- `find_file_path`

## Layered Architecture

### 1. Frontend Control Plane

The frontend is a Next.js application that acts as the operator-facing control plane.

It provides:

- authentication and session bootstrap
- a chat workspace
- per-chat capability selection for agents and MCP tools
- CRUD interfaces for agent and MCP tool definitions
- marketplace publishing, browsing, installation, and removal flows

The chat UI is not just a textbox. It can selectively constrain the runtime by sending `enabled_agent_ids` and `enabled_mcp_tool_ids` in request metadata before a prompt is executed.

### 2. FastAPI API and Ownership Boundary

The backend exposes versioned APIs under `/api/v1` and enforces ownership at the API boundary.

- `/auth` handles register, login, and current-user retrieval
- `/chat` is the orchestrated conversation entrypoint
- `/agents` manages user-owned remote agent definitions
- `/mcp-tools` manages user-owned MCP tool definitions
- `/marketplace` publishes, browses, installs, and removes capability listings

Important behavior implemented in the chat route:

- `user_id` is derived from JWT claims, not trusted from the client body
- a `session_id` is validated or created as a user-owned record
- user-visible capabilities are loaded from the database for each request
- explicit empty allowlists are preserved so disabled capabilities are not silently re-enabled downstream

### 3. Google ADK Orchestration Layer

The AI runtime is centered on a root ADK app built from:

- a discovery agent that decides the routing strategy
- a dynamically configured orchestrator agent that executes the work
- resumable session state shared through ADK

This layer is what turns the system from "chat with tools" into an orchestration runtime:

- planning is separated from execution
- execution shape changes per request
- remote agents and direct MCP tools can coexist inside the same run
- orchestration state is persisted across turns

### 4. A2A Specialist Fleet

Specialists are exposed as remote A2A agents and launched as separate services.

Shared A2A infrastructure includes:

- a common agent factory
- optional JWT validation middleware controlled by `A2A_AUTH_REQUIRED`
- request/response logging middleware
- metadata forwarding for `conversation_history`

If an agent's `authentication_flag` is enabled, the orchestrator forwards the bearer token it received from the main API so downstream services can participate in the same trust boundary.

### 5. MCP Federation Layer

MCP integration is handled through a dedicated adapter that supports:

- `stdio`
- `streamable_http`
- `sse`

The adapter is responsible for:

- environment variable substitution
- connection parameter normalization
- auth header injection when required
- validation and skip logic for broken tool configs

This keeps the tool layer consistent whether capabilities come from YAML defaults or database-backed user records.

### 6. Data and Session State

The persistence model is split by concern:

- PostgreSQL stores users, user-session ownership records, agents, MCP tools, marketplace listings, and installations
- Redis-backed ADK sessions store live orchestration state such as `conversation_history` and `discovery_result`

This division is deliberate. Durable ownership and catalog metadata live in the relational layer, while conversational runtime state lives in the ADK session store used during orchestration and HITL resume flows.

### 7. Marketplace and Installation Model

Marketplace behavior is different for agents and MCP tools:

- agent listings reference a published remote agent record
- installed agents become available to the user by listing association
- MCP tool listings are cloned into user-owned tool records on install
- cloned MCP tools carry `installed_from_listing_id` so provenance is preserved

That model gives users two things at once:

- a distribution mechanism for reusable capabilities
- private customization space for installed MCP tools without mutating the publisher's source definition

## Request Lifecycle

An end-to-end request flows through the system in this order:

1. The frontend sends `/api/v1/chat` with a `session_id`, either a message or HITL approval payload, and optional `enabled_agent_ids` / `enabled_mcp_tool_ids`.
2. FastAPI authenticates the bearer token, derives `user_id`, and validates session ownership.
3. The backend loads the current user's agent and MCP tool catalog from PostgreSQL, including installed capabilities where applicable.
4. Per-chat allowlists are applied, and the surviving capabilities are converted into adapter configs.
5. `RootAgent` builds the ADK runtime with request context, auth token, and user-scoped capability definitions.
6. `tool_agent_discovery` analyzes the prompt and writes a routing decision to `session.state["discovery_result"]`.
7. `Orchestrator` reads that decision and dynamically mounts the selected sub-agents, agent tools, and MCP toolsets.
8. Execution runs across direct MCP calls, remote A2A calls, or both.
9. If a confirmation-gated tool is invoked, the runtime returns a HITL payload instead of completing the action immediately.
10. The frontend renders the HITL approval UI and posts `content.hitl_approval` back to `/api/v1/chat` on the same session.
11. ADK resumes the workflow, conversation history is updated, and the final assistant response is returned.

## Governance and Marketplace Semantics

The project takes governance seriously at the runtime boundary, not just in the UI.

- Users own their agent and MCP tool definitions.
- Session access is enforced server-side through `UserSession` ownership checks.
- Marketplace installs do not bypass ownership rules.
- Self-install is explicitly prevented for marketplace listings.
- Per-chat capability filters are enforced from request metadata before orchestration starts.
- Optional A2A auth allows the main API token to be forwarded to remote specialists when a capability requires it.

This is the difference between a demo and a platform: capabilities are discoverable and composable, but still governed.

## Public Interfaces

### API Surface

| Interface | Purpose |
| --- | --- |
| `/api/v1/auth` | User registration, login, and current-user lookup |
| `/api/v1/chat` | Orchestrated conversations and HITL resume flow |
| `/api/v1/agents` | CRUD for user-owned remote agent definitions |
| `/api/v1/mcp-tools` | CRUD for user-owned MCP tool definitions |
| `/api/v1/marketplace` | Publish, browse, install, uninstall, and remove listings |

### Chat Metadata

The chat interface supports request-scoped capability control through metadata:

- `enabled_agent_ids`
- `enabled_mcp_tool_ids`

These allow the frontend to narrow the execution catalog for a single conversation without mutating the user's saved catalog.

### Service Ports

| Service | Port |
| --- | ---: |
| Main API | 8000 |
| Job Search | 8001 |
| GitHub Assistant | 8002 |
| Filesystem Assistant | 8003 |
| Web Research Assistant | 8004 |
| Knowledge Manager | 8005 |
| Database Analyst | 8006 |
| Reasoning Assistant | 8007 |
| Browser Automation | 8008 |
| Git Assistant | 8009 |
| Time Assistant | 8010 |
| Report Writer | 8011 |

## Repository Structure

```text
MultiAgentIntegration App/
|-- backend_service/
|   |-- app/
|   |   |-- api/v1/routes/      # auth, chat, agents, MCP tools, marketplace
|   |   |-- agentic/            # orchestrator, adapters, prompts, specialists, tools
|   |   |-- services/           # business logic and ownership enforcement
|   |   |-- models/             # ORM models and API schemas
|   |   `-- db/                 # async SQLAlchemy engine and metadata
|   |-- scripts/                # demo bootstrap and marketplace seeding
|   |-- ProjectSetup/           # backend, frontend, and PostgreSQL setup guides
|   `-- documentation/          # architecture diagrams
|-- frontend/
|   |-- src/app/                # route groups for auth and dashboard screens
|   |-- src/components/         # chat, marketplace, agents, MCP tools, layout
|   |-- src/store/              # Redux store, slices, and RTK Query APIs
|   `-- src/lib/                # shared auth helpers and types
`-- README.md
```

## Quick Start

For full environment setup, use the guides in:

- [backend_service/ProjectSetup/README.md](backend_service/ProjectSetup/README.md)
- [backend_service/ProjectSetup/BACKEND_SETUP.md](backend_service/ProjectSetup/BACKEND_SETUP.md)
- [backend_service/ProjectSetup/FRONTEND_SETUP.md](backend_service/ProjectSetup/FRONTEND_SETUP.md)
- [backend_service/ProjectSetup/POSTGRES_SETUP.md](backend_service/ProjectSetup/POSTGRES_SETUP.md)

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL
- Redis for ADK session persistence
- Windows PowerShell and Windows Terminal if you want to use the provided multi-service launcher

Current runtime note: the backend instantiates `google.adk_community.sessions.RedisSessionService`, so stateful chat, resumability, and HITL resume depend on Redis being available.

### 1. Set Up the Backend

```powershell
cd backend_service
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create `backend_service/.env` with at least:

```env
GOOGLE_API_KEY=your_google_api_key
DATABASE_URL=postgresql+asyncpg://admin:admin@localhost:5432/my_db
SECRET_KEY=replace-with-a-strong-secret
```

Optional runtime flags you will likely use during local development:

```env
A2A_AUTH_REQUIRED=false
ORCHESTRATOR_ENABLE_DIRECT_MCP_TOOLS=false
```

### 2. Bootstrap the Database and Demo Catalog

```powershell
alembic upgrade head
python -m scripts.init_db
python -m scripts.seed_agent_listings
python -m scripts.migrate_and_seed_marketplace
```

What these commands do:

- apply schema migrations
- reset and seed demo users
- seed the 11 remote agent listings
- seed the 10 MCP tool listings and publish them to the marketplace

### 3. Start the Services

Start only the main API:

```powershell
python run.py
```

Or start the full multi-agent stack in Windows Terminal tabs:

```powershell
.\start_all_agents.ps1
```

Main API endpoints:

- app: `http://127.0.0.1:8000`
- docs: `http://127.0.0.1:8000/docs`

### 4. Set Up the Frontend

```powershell
cd ..\frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Run the UI:

```powershell
npm run dev
```

Then open:

```text
http://localhost:3000
```

## Why This Architecture Is Useful

MultiAgentIntegration App is interesting because it treats AI execution as a runtime system, not as a single prompt surface.

- planning is explicit
- execution is dynamically composed
- capabilities are user-scoped and marketplace-distributed
- human approval is a first-class control flow, not an afterthought
- state survives across turns and interrupted workflows

That makes the project a solid reference for teams building governed, extensible, multi-agent systems instead of isolated tool-calling demos.

