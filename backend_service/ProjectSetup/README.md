# Project Setup Docs

This folder contains local setup guides for TheOrchestrator.

Available guides:

- [POSTGRES_SETUP.md](d:/projects/TheOrchestrator/backend_service/ProjectSetup/POSTGRES_SETUP.md): Run PostgreSQL locally with Docker.
- [BACKEND_SETUP.md](d:/projects/TheOrchestrator/backend_service/ProjectSetup/BACKEND_SETUP.md): Set up the FastAPI backend, database bootstrap, and multi-agent services.
- [FRONTEND_SETUP.md](d:/projects/TheOrchestrator/backend_service/ProjectSetup/FRONTEND_SETUP.md): Set up and run the Next.js UI.

Recommended order:

1. Complete PostgreSQL setup.
2. Complete backend setup and verify the API on port `8000`.
3. Start the agent services if you want orchestrated multi-agent chat.
4. Complete frontend setup and open the UI on port `3000`.