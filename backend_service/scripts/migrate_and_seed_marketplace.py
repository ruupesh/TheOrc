"""One-time script: add marketplace columns + seed 10 MCP tool listings."""

import asyncio
import uuid
from sqlalchemy import text
from app.db.database import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as db:
        # ── 1. Check existing columns ────────────────────────────────────
        r = await db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'marketplace_listings' ORDER BY ordinal_position"
        ))
        cols = [row[0] for row in r.fetchall()]
        print("Current columns:", cols)

        # ── 2. Add missing columns ───────────────────────────────────────
        if "mcp_tool_id" not in cols:
            await db.execute(text(
                "ALTER TABLE marketplace_listings "
                "ADD COLUMN mcp_tool_id UUID REFERENCES mcp_tools(id) ON DELETE CASCADE"
            ))
            await db.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_marketplace_listings_mcp_tool_id "
                "ON marketplace_listings(mcp_tool_id)"
            ))
            print("Added mcp_tool_id column")

        if "item_type" not in cols:
            await db.execute(text(
                "ALTER TABLE marketplace_listings "
                "ADD COLUMN item_type VARCHAR(20) NOT NULL DEFAULT 'agent'"
            ))
            print("Added item_type column")

        if "visibility" not in cols:
            await db.execute(text(
                "ALTER TABLE marketplace_listings "
                "ADD COLUMN visibility VARCHAR(20) NOT NULL DEFAULT 'public'"
            ))
            print("Added visibility column")

        # Make agent_id nullable (was NOT NULL)
        if "agent_id" in cols:
            await db.execute(text(
                "ALTER TABLE marketplace_listings ALTER COLUMN agent_id DROP NOT NULL"
            ))
            print("Made agent_id nullable")

        await db.commit()

        # ── 3. Verify columns ────────────────────────────────────────────
        r = await db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'marketplace_listings' ORDER BY ordinal_position"
        ))
        print("Updated columns:", [row[0] for row in r.fetchall()])

        # ── 4. Get users ─────────────────────────────────────────────────
        r = await db.execute(text("SELECT id, username FROM users WHERE username IN ('user1', 'user2')"))
        users = {row[1]: row[0] for row in r.fetchall()}
        print(f"Users: {users}")
        if "user1" not in users or "user2" not in users:
            print("ERROR: user1 and/or user2 not found in database!")
            return

        # ── 5. Get MCP tools (ordered by name) ──────────────────────────
        r = await db.execute(text("SELECT id, name FROM mcp_tools ORDER BY name"))
        tools = r.fetchall()
        print(f"MCP tools ({len(tools)}):")
        for t in tools:
            print(f"  {t[0]} | {t[1]}")

        # ── 6. Check existing listings ───────────────────────────────────
        r = await db.execute(text("SELECT mcp_tool_id FROM marketplace_listings WHERE mcp_tool_id IS NOT NULL"))
        existing = {row[0] for row in r.fetchall()}
        print(f"Existing MCP tool listings: {len(existing)}")

        # ── 7. Seed: first 5 tools → user1, last 5 → user2 ─────────────
        descriptions = {
            "duckduckgo_search": "Web search powered by DuckDuckGo — search the web privately without tracking.",
            "fetch": "HTTP fetch tool — make HTTP requests to retrieve data from any URL.",
            "filesystem": "Filesystem access tool — read, write, list, and manage files and directories.",
            "git": "Git version control tool — clone, commit, push, pull, and manage repositories.",
            "github": "GitHub integration tool — manage repos, issues, PRs, and GitHub actions.",
            "memory": "Persistent memory tool — store and retrieve key-value data across sessions.",
            "puppeteer": "Browser automation via Puppeteer — navigate pages, click elements, take screenshots.",
            "sequential_thinking": "Step-by-step reasoning tool — break down complex problems into sequential thoughts.",
            "sqlite": "SQLite database tool — execute queries, manage tables, and analyze local databases.",
            "time": "Time and timezone tool — get current time, convert timezones, and calculate durations.",
        }

        user1_id = users["user1"]
        user2_id = users["user2"]

        inserted = 0
        for i, (tool_id, tool_name) in enumerate(tools):
            if tool_id in existing:
                print(f"  Skipping {tool_name} (already listed)")
                continue

            publisher_id = user1_id if i < 5 else user2_id
            publisher_name = "user1" if i < 5 else "user2"
            desc = descriptions.get(tool_name, f"MCP tool: {tool_name}")

            await db.execute(text(
                "INSERT INTO marketplace_listings "
                "(id, mcp_tool_id, publisher_id, item_type, visibility, title, description, is_published, created_at) "
                "VALUES (:id, :mcp_tool_id, :publisher_id, 'mcp_tool', 'public', :title, :description, true, NOW())"
            ), {
                "id": str(uuid.uuid4()),
                "mcp_tool_id": str(tool_id),
                "publisher_id": str(publisher_id),
                "title": tool_name.replace("_", " ").title(),
                "description": desc,
            })
            inserted += 1
            print(f"  Published '{tool_name}' as public from {publisher_name}")

        await db.commit()
        print(f"\nDone! Inserted {inserted} marketplace listings.")

        # ── 8. Final verification ────────────────────────────────────────
        r = await db.execute(text(
            "SELECT ml.title, ml.item_type, ml.visibility, u.username "
            "FROM marketplace_listings ml "
            "JOIN users u ON u.id = ml.publisher_id "
            "ORDER BY ml.title"
        ))
        print("\nAll marketplace listings:")
        for row in r.fetchall():
            print(f"  {row[0]} | type={row[1]} | visibility={row[2]} | publisher={row[3]}")


if __name__ == "__main__":
    asyncio.run(main())
