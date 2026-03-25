"""Step 1 script: clear DB and create demo users.

This script is intentionally destructive for local demo setup.
It performs a full data wipe (rows only, not schema) and then creates
exactly three users with known credentials.

Run from backend_service:
    python -m scripts.init_db
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path for imports when running as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import delete

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.database import AsyncSessionLocal, engine
from app.models.agent import Agent
from app.models.marketplace import MarketplaceListing, UserAgentInstallation
from app.models.mcp_tool import McpTool
from app.models.user import User
from app.models.user_session import UserSession


DEMO_USERS = [
    {"email": "user1@example.com", "username": "user1", "password": "user1234"},
    {"email": "user2@example.com", "username": "user2", "password": "user1234"},
    {"email": "user3@example.com", "username": "user3", "password": "user1234"},
]


async def ensure_tables_exist() -> None:
    """Create tables if they do not exist yet.

    We keep this here so teammates can run this script on a fresh local DB
    without requiring a separate migration step for demo setup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def clear_all_data(session) -> None:
    """Remove all data rows in a foreign-key-safe order.

    We delete child records first to make behavior explicit and easy to follow.
    """
    print("[1/3] Clearing existing database rows...")

    await session.execute(delete(UserAgentInstallation))
    await session.execute(delete(MarketplaceListing))
    await session.execute(delete(Agent))
    await session.execute(delete(McpTool))
    await session.execute(delete(UserSession))
    await session.execute(delete(User))

    await session.commit()
    print("      Database cleared.")


async def seed_demo_users(session) -> None:
    """Create the three fixed demo users required for app demo."""
    print("[2/3] Creating demo users...")

    for user in DEMO_USERS:
        session.add(
            User(
                email=user["email"],
                username=user["username"],
                hashed_password=get_password_hash(user["password"]),
                is_active=True,
            )
        )

    await session.commit()
    print("      Created users: user1, user2, user3")


async def main() -> None:
    print("=" * 72)
    print("Step 1 - Reset DB and Seed Users")
    print("=" * 72)

    await ensure_tables_exist()

    async with AsyncSessionLocal() as session:
        await clear_all_data(session)
        await seed_demo_users(session)

    await engine.dispose()
    print("[3/3] Done.")
    print("Next: run `python -m scripts.seed_agents_and_market`")


if __name__ == "__main__":
    asyncio.run(main())
