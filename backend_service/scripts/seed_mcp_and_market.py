"""Step 3 script: seed MCP tools and publish all to marketplace.

Distribution rule for demo users:
- Use MCP tools from mcp_conf.yml
- Distribute as equally as possible across user1/user2/user3
  (for 10 tools this becomes 4/3/3 via round-robin)

Run from backend_service:
    python -m scripts.migrate_and_seed_marketplace
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path for imports when running as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import delete, select

from app.agentic.adapters.mcp_adapter import get_mcp_conf
from app.db.database import AsyncSessionLocal, engine
from app.models.marketplace import MarketplaceListing
from app.models.mcp_tool import McpTool
from app.models.user import User


USER_ORDER = [
    ("user1", "user1@example.com"),
    ("user2", "user2@example.com"),
    ("user3", "user3@example.com"),
]

TOOL_DESCRIPTIONS = {
    "duckduckgo_search": "Web search powered by DuckDuckGo — search privately without tracking.",
    "fetch": "HTTP fetch tool — make HTTP requests and retrieve data from URLs.",
    "filesystem": "Filesystem tool — read, write, list, and manage files/directories.",
    "git": "Git tool — clone, diff, commit, and inspect repositories.",
    "github": "GitHub tool — work with repos, issues, pull requests, and actions.",
    "memory": "Memory tool — store and retrieve key-value context across sessions.",
    "puppeteer": "Browser automation tool — navigate pages and automate interactions.",
    "sequential_thinking": "Reasoning tool — break complex tasks into explicit thought steps.",
    "sqlite": "SQLite tool — execute queries and inspect local database data.",
    "time": "Time tool — current time, timezone conversion, and duration calculations.",
}


async def get_required_users(session) -> list[tuple[str, User]]:
    """Fetch users in stable order and fail fast if missing."""
    ordered_users: list[tuple[str, User]] = []
    for username, email in USER_ORDER:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise RuntimeError(
                f"Required user '{email}' not found. Run scripts.init_db first."
            )
        ordered_users.append((username, user))
    return ordered_users


async def clear_mcp_data(session) -> None:
    """Clear existing MCP listings and non-system MCP tools before re-seeding."""
    print("[1/4] Clearing existing MCP listings and non-system MCP tools...")
    await session.execute(
        delete(MarketplaceListing).where(MarketplaceListing.item_type == "mcp_tool")
    )
    await session.execute(delete(McpTool).where(McpTool.is_system == False))
    await session.commit()
    print("      MCP data cleared.")


async def seed_mcp_tools_and_publish(session, ordered_users: list[tuple[str, User]]) -> None:
    """Seed MCP tools from YAML and publish each to marketplace."""
    print("[2/4] Seeding MCP tools from mcp_conf.yml...")

    # Read authoritative MCP tool list from YAML so DB seed mirrors runtime config.
    configs = sorted(get_mcp_conf(), key=lambda cfg: cfg["name"])

    for idx, cfg in enumerate(configs):
        # Round-robin assignment for near-equal distribution among three users.
        owner_username, owner = ordered_users[idx % len(ordered_users)]

        tool = McpTool(
            owner_id=owner.id,
            name=cfg["name"],
            connection_type=cfg["connection_type"],
            command=cfg.get("command"),
            args=cfg.get("args"),
            env=cfg.get("env"),
            url=cfg.get("url"),
            headers=cfg.get("headers"),
            sse_read_timeout=float(cfg.get("sse_read_timeout", 300.0)),
            timeout=float(cfg.get("timeout", 30.0)),
            authentication_flag=bool(cfg.get("authentication_flag", False)),
            auth_token=cfg.get("auth_token"),
            tool_filter=cfg.get("tool_filter"),
            is_system=False,
        )
        session.add(tool)
        await session.flush()  # Flush so `tool.id` is available for listing.

        session.add(
            MarketplaceListing(
                mcp_tool_id=tool.id,
                publisher_id=owner.id,
                item_type="mcp_tool",
                visibility="public",
                title=cfg["name"].replace("_", " ").title(),
                description=TOOL_DESCRIPTIONS.get(
                    cfg["name"], f"MCP tool: {cfg['name']}"
                ),
                is_published=True,
            )
        )

        print(f"      Seeded {cfg['name']} -> {owner_username}, published")

    await session.commit()


async def print_summary(session, ordered_users: list[tuple[str, User]]) -> None:
    """Print tool counts by owner for quick verification."""
    print("[3/4] Summary:")
    for username, user in ordered_users:
        result = await session.execute(
            select(McpTool).where(McpTool.owner_id == user.id, McpTool.is_system == False)
        )
        count = len(result.scalars().all())
        print(f"      {username}: {count} MCP tools")


async def main() -> None:
    print("=" * 72)
    print("Step 3 - Seed MCP Tools and Publish to Marketplace")
    print("=" * 72)

    async with AsyncSessionLocal() as session:
        ordered_users = await get_required_users(session)
        await clear_mcp_data(session)
        await seed_mcp_tools_and_publish(session, ordered_users)
        await print_summary(session, ordered_users)

    await engine.dispose()
    print("[4/4] Done.")


if __name__ == "__main__":
    asyncio.run(main())
