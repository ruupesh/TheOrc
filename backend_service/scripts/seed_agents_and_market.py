"""Step 2 script: seed agents with ownership split and publish all to marketplace.

Ownership rules requested for demo:
- user1 owns ports 8001..8004 (4 agents)
- user2 owns ports 8005..8007 (3 agents)
- user3 owns ports 8008..8011 (4 agents)

Run from backend_service:
    python -m scripts.seed_agent_listings
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path for imports when running as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import delete, select

from app.agentic.adapters.remote_a2a_adapter import get_remote_a2a_conf
from app.db.database import AsyncSessionLocal, engine
from app.models.agent import Agent
from app.models.marketplace import MarketplaceListing
from app.models.user import User


USER_EMAILS = {
    "user1": "user1@example.com",
    "user2": "user2@example.com",
    "user3": "user3@example.com",
}


def owner_for_port(port: int) -> str:
    """Map agent port to owner username based on the requested split."""
    if 8001 <= port <= 8004:
        return "user1"
    if 8005 <= port <= 8007:
        return "user2"
    if 8008 <= port <= 8011:
        return "user3"
    raise ValueError(f"Unexpected agent port {port}. Expected 8001..8011")


async def get_required_users(session) -> dict[str, User]:
    """Fetch and validate that all three demo users exist."""
    users: dict[str, User] = {}
    for username, email in USER_EMAILS.items():
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise RuntimeError(
                f"Required user '{email}' not found. Run scripts.init_db first."
            )
        users[username] = user
    return users


async def clear_agent_data(session) -> None:
    """Clear existing agent listings and non-system agents before re-seeding."""
    print("[1/4] Clearing existing agent listings and non-system agents...")
    await session.execute(
        delete(MarketplaceListing).where(MarketplaceListing.item_type == "agent")
    )
    await session.execute(delete(Agent).where(Agent.is_system == False))
    await session.commit()
    print("      Agent data cleared.")


async def seed_agents_and_publish(session, users: dict[str, User]) -> None:
    """Seed agents from remote config and publish each one to marketplace."""
    print("[2/4] Seeding agents from remote_agents_conf.yml...")

    # Read authoritative agent list from YAML so DB seed always mirrors runtime config.
    configs = sorted(get_remote_a2a_conf(), key=lambda cfg: int(cfg["port"]))

    if len(configs) != 11:
        raise RuntimeError(
            f"Expected 11 agents in remote config, found {len(configs)}"
        )

    for cfg in configs:
        port = int(cfg["port"])
        owner_username = owner_for_port(port)
        owner = users[owner_username]

        agent = Agent(
            owner_id=owner.id,
            name=cfg["name"],
            description=cfg["description"],
            host=cfg["host"],
            port=port,
            agent_card_path=cfg.get("agent_card_path", "/.well-known/agent.json"),
            timeout=float(cfg.get("timeout", 300.0)),
            full_history=bool(cfg.get("full_history", True)),
            authentication_flag=bool(cfg.get("authentication_flag", False)),
            allow_conversation_history=bool(
                cfg.get("allow_conversation_history", True)
            ),
            is_system=False,
        )
        session.add(agent)
        await session.flush()  # Flush so `agent.id` is available for listing.

        session.add(
            MarketplaceListing(
                agent_id=agent.id,
                publisher_id=owner.id,
                item_type="agent",
                visibility="public",
                title=cfg["name"].replace("_", " ").title(),
                description=cfg["description"],
                is_published=True,
            )
        )

        print(
            f"      Seeded {cfg['name']} (port {port}) -> {owner_username}, published"
        )

    await session.commit()


async def print_summary(session, users: dict[str, User]) -> None:
    """Print counts by owner for easy verification in terminal output."""
    print("[3/4] Summary:")
    for username, user in users.items():
        result = await session.execute(
            select(Agent).where(Agent.owner_id == user.id, Agent.is_system == False)
        )
        count = len(result.scalars().all())
        print(f"      {username}: {count} agents")


async def main() -> None:
    print("=" * 72)
    print("Step 2 - Seed Agents and Publish to Marketplace")
    print("=" * 72)

    async with AsyncSessionLocal() as session:
        users = await get_required_users(session)
        await clear_agent_data(session)
        await seed_agents_and_publish(session, users)
        await print_summary(session, users)

    await engine.dispose()
    print("[4/4] Done.")
    print("Next: run `python -m scripts.migrate_and_seed_marketplace`")


if __name__ == "__main__":
    asyncio.run(main())
