from fastapi import APIRouter

from app.api.v1.routes import auth, chat, agents, mcp_tools, marketplace

api_v1_router = APIRouter()
api_v1_router.include_router(auth.router, tags=["Authentication"])
api_v1_router.include_router(chat.router, tags=["Chat"])
api_v1_router.include_router(agents.router, tags=["Agents"])
api_v1_router.include_router(mcp_tools.router, tags=["MCP Tools"])
api_v1_router.include_router(marketplace.router, tags=["Marketplace"])
