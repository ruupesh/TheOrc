"""
Database initialization and seed script.

Creates all tables and seeds the default agents/MCP tools from YAML config files.
Run:  python -m scripts.init_db
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select
from app.db.database import engine, AsyncSessionLocal
from app.db.base import Base
from app.models.user import User
from app.models.user_session import UserSession  # noqa: F401
from app.models.agent import Agent
from app.models.mcp_tool import McpTool
from app.models.marketplace import MarketplaceListing, UserAgentInstallation  # noqa: F401
from app.core.security import get_password_hash
from app.agentic.adapters.remote_a2a_adapter import get_remote_a2a_conf
from app.agentic.adapters.mcp_adapter import get_mcp_conf


SYSTEM_USER_EMAIL = "system@orchestrator.local"
SYSTEM_USER_USERNAME = "system"
SYSTEM_USER_PASSWORD = "SystemUser2026"


async def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")


async def get_or_create_system_user(session) -> User:
    """Get or create the system user who owns default agents/tools."""
    result = await session.execute(
        select(User).where(User.email == SYSTEM_USER_EMAIL)
    )
    user = result.scalar_one_or_none()
    if user:
        print(f"System user already exists: {user.id}")
        return user

    user = User(
        email=SYSTEM_USER_EMAIL,
        username=SYSTEM_USER_USERNAME,
        hashed_password=get_password_hash(SYSTEM_USER_PASSWORD),
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    print(f"System user created: {user.id}")
    return user


async def seed_agents(session, system_user: User):
    """Seed agents from remote_agents_conf.yml."""
    print("Seeding agents from remote_agents_conf.yml...")

    # Check if agents already seeded
    result = await session.execute(
        select(Agent).where(Agent.is_system == True).limit(1)
    )
    if result.scalar_one_or_none():
        print("  System agents already exist, skipping seed.")
        return

    configs = get_remote_a2a_conf()
    count = 0
    for cfg in configs:
        agent = Agent(
            owner_id=system_user.id,
            name=cfg["name"],
            description=cfg["description"],
            host=cfg["host"],
            port=cfg["port"],
            agent_card_path=cfg.get("agent_card_path", "/.well-known/agent.json"),
            timeout=cfg.get("timeout", 300.0),
            full_history=cfg.get("full_history", True),
            authentication_flag=cfg.get("authentication_flag", False),
            allow_conversation_history=cfg.get("allow_conversation_history", True),
            is_system=True,
        )
        session.add(agent)
        count += 1

    await session.commit()
    print(f"  Seeded {count} agents.")


async def seed_mcp_tools(session, system_user: User):
    """Seed MCP tools from mcp_conf.yml."""
    print("Seeding MCP tools from mcp_conf.yml...")

    # Check if tools already seeded
    result = await session.execute(
        select(McpTool).where(McpTool.is_system == True).limit(1)
    )
    if result.scalar_one_or_none():
        print("  System MCP tools already exist, skipping seed.")
        return

    configs = get_mcp_conf()
    count = 0
    for cfg in configs:
        tool = McpTool(
            owner_id=system_user.id,
            name=cfg["name"],
            connection_type=cfg["connection_type"],
            command=cfg.get("command"),
            args=cfg.get("args"),
            env=cfg.get("env"),
            url=cfg.get("url"),
            headers=cfg.get("headers"),
            sse_read_timeout=cfg.get("sse_read_timeout", 300.0),
            timeout=cfg.get("timeout", 30.0),
            authentication_flag=cfg.get("authentication_flag", False),
            auth_token=cfg.get("auth_token"),
            tool_filter=cfg.get("tool_filter"),
            is_system=True,
        )
        session.add(tool)
        count += 1

    await session.commit()
    print(f"  Seeded {count} MCP tools.")


async def main():
    print("=" * 60)
    print("TheOrchestrator Database Initialization")
    print("=" * 60)

    await create_tables()

    async with AsyncSessionLocal() as session:
        system_user = await get_or_create_system_user(session)
        await seed_agents(session, system_user)
        await seed_mcp_tools(session, system_user)

    await engine.dispose()
    print("=" * 60)
    print("Initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
