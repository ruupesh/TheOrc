"""Seed the 11 real agentic agents into the marketplace for user1 and user2."""
import asyncio
import uuid

from sqlalchemy import text
from app.db.database import AsyncSessionLocal


# All 11 agents from remote_agents_conf.yml
# (name, description, port)
REAL_AGENTS = [
    ("job_search_assistant",
     "A job search agent that finds job opportunities and saves the results to disk.",
     8001),
    ("github_assistant",
     "A GitHub operations agent that manages repositories, issues, pull requests, and performs code search across GitHub.",
     8002),
    ("filesystem_assistant",
     "A filesystem operations agent that explores, reads, writes, searches, and manages files and directories on the local system.",
     8003),
    ("web_research_assistant",
     "A web research agent that fetches, analyzes, and summarizes content from any public web page or API endpoint.",
     8004),
    ("knowledge_manager",
     "A knowledge management agent that maintains a persistent knowledge graph with entities, observations, and relations for long-term memory.",
     8005),
    ("database_analyst",
     "A database analyst agent that executes SQL queries, designs schemas, analyzes data, and manages SQLite databases.",
     8006),
    ("reasoning_assistant",
     "A reasoning and problem-solving agent that uses structured sequential thinking to break down complex problems, analyze decisions, debug issues, and plan tasks.",
     8007),
    ("browser_automation",
     "A browser automation agent that navigates web pages, takes screenshots, fills forms, extracts content, and performs web testing using a headless Chrome browser.",
     8008),
    ("git_assistant",
     "A Git operations agent that analyzes commit history, shows diffs, manages branches, performs blame analysis, and investigates code changes in Git repositories.",
     8009),
    ("time_assistant",
     "A time and timezone agent that provides current times, converts between timezones, helps schedule meetings across zones, and performs date/time calculations.",
     8010),
    ("report_writer",
     "A report writing agent that researches topics from the web and produces well-structured, professional reports saved to disk in Markdown format.",
     8011),
]

# Split: first 6 → user1, last 5 → user2; most public, a couple private
ASSIGNMENTS = [
    # (index, username, visibility)
    (0, "user1", "public"),   # job_search_assistant
    (1, "user1", "public"),   # github_assistant
    (2, "user1", "public"),   # filesystem_assistant
    (3, "user1", "public"),   # web_research_assistant
    (4, "user1", "public"),   # knowledge_manager
    (5, "user1", "private"),  # database_analyst
    (6, "user2", "public"),   # reasoning_assistant
    (7, "user2", "public"),   # browser_automation
    (8, "user2", "public"),   # git_assistant
    (9, "user2", "public"),   # time_assistant
    (10, "user2", "private"), # report_writer
]


async def main():
    async with AsyncSessionLocal() as db:
        # ── 1. Clean up previously seeded fake agents ──
        print("Cleaning up previously seeded fake agent listings and agents...")
        await db.execute(text(
            "DELETE FROM marketplace_listings WHERE item_type = 'agent'"
        ))
        # Delete non-system agents that are NOT owned by the 'system' user
        await db.execute(text(
            "DELETE FROM agents WHERE is_system = false "
            "AND owner_id != (SELECT id FROM users WHERE username = 'system')"
        ))
        print("  Done.")

        # ── 2. Get user IDs ──
        r = await db.execute(text(
            "SELECT id, username FROM users WHERE username IN ('user1', 'user2')"
        ))
        users = {row[1]: row[0] for row in r.fetchall()}
        print(f"Users: {users}")

        # ── 3. Insert real agents + marketplace listings ──
        for idx, username, vis in ASSIGNMENTS:
            name, desc, port = REAL_AGENTS[idx]
            owner_id = users[username]
            agent_id = str(uuid.uuid4())

            await db.execute(text(
                "INSERT INTO agents (id, owner_id, name, description, host, port, "
                "agent_card_path, timeout, full_history, authentication_flag, "
                "allow_conversation_history, is_system, created_at) "
                "VALUES (:id, :owner_id, :name, :desc, 'http://localhost', :port, "
                "'/.well-known/agent.json', 300.0, true, true, true, false, NOW())"
            ), {
                "id": agent_id,
                "owner_id": str(owner_id),
                "name": name,
                "desc": desc,
                "port": port,
            })

            listing_id = str(uuid.uuid4())
            title = name.replace("_", " ").title()
            await db.execute(text(
                "INSERT INTO marketplace_listings "
                "(id, agent_id, publisher_id, item_type, visibility, title, "
                "description, is_published, created_at) "
                "VALUES (:id, :agent_id, :pub_id, 'agent', :vis, :title, "
                ":desc, true, NOW())"
            ), {
                "id": listing_id,
                "agent_id": agent_id,
                "pub_id": str(owner_id),
                "vis": vis,
                "title": title,
                "desc": desc,
            })
            print(f"  Published: {name} (port {port}, {vis}) → {username}")

        await db.commit()
        print(f"\nDone! {len(ASSIGNMENTS)} real agents created and published.")

        # ── 4. Verify ──
        r = await db.execute(text(
            "SELECT ml.title, ml.item_type, ml.visibility, u.username "
            "FROM marketplace_listings ml JOIN users u ON u.id = ml.publisher_id "
            "WHERE ml.item_type = 'agent' ORDER BY ml.title"
        ))
        print("\nAgent listings in marketplace:")
        for row in r.fetchall():
            print(f"  {row[0]} | {row[2]} | by {row[3]}")


if __name__ == "__main__":
    asyncio.run(main())
