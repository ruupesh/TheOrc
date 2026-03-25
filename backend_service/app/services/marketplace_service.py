"""Marketplace service — publish, browse, install, and uninstall agents and MCP tools."""

from copy import deepcopy
import uuid
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.agent import Agent
from app.models.mcp_tool import McpTool
from app.models.marketplace import MarketplaceListing, UserAgentInstallation
from app.utils.logging import logger


def _clone_mcp_tool_for_user(
    source_tool: McpTool,
    installing_user_id: uuid.UUID,
    listing_id: uuid.UUID,
) -> McpTool:
    """Create a user-owned MCP tool copy from a marketplace listing source tool."""
    return McpTool(
        owner_id=installing_user_id,
        installed_from_listing_id=listing_id,
        name=source_tool.name,
        connection_type=source_tool.connection_type,
        command=source_tool.command,
        args=deepcopy(source_tool.args),
        env=deepcopy(source_tool.env),
        url=source_tool.url,
        headers=deepcopy(source_tool.headers),
        sse_read_timeout=source_tool.sse_read_timeout,
        timeout=source_tool.timeout,
        authentication_flag=source_tool.authentication_flag,
        auth_token=None,
        tool_filter=deepcopy(source_tool.tool_filter),
        is_system=False,
    )


async def publish_item(
    db: AsyncSession,
    publisher_id: uuid.UUID,
    title: str,
    description: str,
    visibility: str = "public",
    agent_id: Optional[uuid.UUID] = None,
    mcp_tool_id: Optional[uuid.UUID] = None,
) -> MarketplaceListing:
    """Publish a user's agent or MCP tool to the marketplace.

    Exactly one of agent_id or mcp_tool_id must be provided.
    Raises ValueError on invalid input.
    """
    if not agent_id and not mcp_tool_id:
        raise ValueError("Either agent_id or mcp_tool_id is required")
    if agent_id and mcp_tool_id:
        raise ValueError("Provide only one of agent_id or mcp_tool_id")

    if agent_id:
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id, Agent.owner_id == publisher_id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("Agent not found or you don't own this agent")
        result = await db.execute(
            select(MarketplaceListing).where(MarketplaceListing.agent_id == agent_id)
        )
        if result.scalar_one_or_none():
            raise ValueError("This agent is already published to the marketplace")
        item_type = "agent"
    else:
        result = await db.execute(
            select(McpTool).where(McpTool.id == mcp_tool_id, McpTool.owner_id == publisher_id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("MCP tool not found or you don't own this tool")
        result = await db.execute(
            select(MarketplaceListing).where(MarketplaceListing.mcp_tool_id == mcp_tool_id)
        )
        if result.scalar_one_or_none():
            raise ValueError("This MCP tool is already published to the marketplace")
        item_type = "mcp_tool"

    listing = MarketplaceListing(
        agent_id=agent_id,
        mcp_tool_id=mcp_tool_id,
        publisher_id=publisher_id,
        item_type=item_type,
        visibility=visibility,
        title=title,
        description=description,
    )
    db.add(listing)
    await db.commit()
    await db.refresh(listing)
    logger.info(
        "Item published to marketplace",
        listing_id=str(listing.id),
        item_type=item_type,
    )
    return listing


# Keep backward-compatible alias
async def publish_agent(
    db: AsyncSession,
    publisher_id: uuid.UUID,
    agent_id: uuid.UUID,
    title: str,
    description: str,
) -> MarketplaceListing:
    return await publish_item(db, publisher_id, title, description, "public", agent_id=agent_id)


async def list_marketplace(
    db: AsyncSession,
    current_user_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[MarketplaceListing]:
    """Browse published marketplace listings. Shows public items + user's own private items."""
    query = (
        select(MarketplaceListing)
        .options(
            selectinload(MarketplaceListing.agent),
            selectinload(MarketplaceListing.mcp_tool),
            selectinload(MarketplaceListing.publisher),
        )
        .where(MarketplaceListing.is_published == True)
    )

    # Visibility filter: public listings OR the current user's own private listings
    if current_user_id:
        query = query.where(
            or_(
                MarketplaceListing.visibility == "public",
                MarketplaceListing.publisher_id == current_user_id,
            )
        )
    else:
        query = query.where(MarketplaceListing.visibility == "public")

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            MarketplaceListing.title.ilike(search_filter)
            | MarketplaceListing.description.ilike(search_filter)
        )

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_listing_by_id(
    db: AsyncSession, listing_id: uuid.UUID
) -> Optional[MarketplaceListing]:
    """Get a marketplace listing by ID with related data."""
    result = await db.execute(
        select(MarketplaceListing)
        .options(selectinload(MarketplaceListing.agent), selectinload(MarketplaceListing.publisher))
        .where(MarketplaceListing.id == listing_id)
    )
    return result.scalar_one_or_none()


async def install_agent(
    db: AsyncSession, user_id: uuid.UUID, listing_id: uuid.UUID
) -> UserAgentInstallation:
    """Install a marketplace agent into the user's orchestrator.

    Raises ValueError if listing not found, not published, or already installed.
    """
    # Verify the listing exists and is published
    result = await db.execute(
        select(MarketplaceListing).where(
            MarketplaceListing.id == listing_id,
            MarketplaceListing.is_published == True,
        )
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise ValueError("Marketplace listing not found or not published")

    # Prevent self-install
    if listing.publisher_id == user_id:
        raise ValueError("You cannot install your own listing")

    # Check if already installed
    result = await db.execute(
        select(UserAgentInstallation).where(
            UserAgentInstallation.user_id == user_id,
            UserAgentInstallation.listing_id == listing_id,
        )
    )
    if result.scalar_one_or_none():
        raise ValueError("Agent is already installed")

    if listing.item_type == "mcp_tool":
        if not listing.mcp_tool_id:
            raise ValueError("Invalid MCP tool listing")

        source_result = await db.execute(
            select(McpTool).where(McpTool.id == listing.mcp_tool_id)
        )
        source_tool = source_result.scalar_one_or_none()
        if not source_tool:
            raise ValueError("Source MCP tool for listing not found")

        installed_copy = _clone_mcp_tool_for_user(
            source_tool=source_tool,
            installing_user_id=user_id,
            listing_id=listing.id,
        )
        db.add(installed_copy)

    installation = UserAgentInstallation(
        user_id=user_id,
        listing_id=listing_id,
    )
    db.add(installation)
    await db.commit()
    await db.refresh(installation)
    logger.info(
        "Agent installed from marketplace",
        user_id=str(user_id),
        listing_id=str(listing_id),
    )
    return installation


async def uninstall_agent(
    db: AsyncSession, user_id: uuid.UUID, installation_id: uuid.UUID
) -> bool:
    """Remove an installed marketplace agent."""
    result = await db.execute(
        select(UserAgentInstallation).where(
            UserAgentInstallation.id == installation_id,
            UserAgentInstallation.user_id == user_id,
        )
    )
    installation = result.scalar_one_or_none()
    if not installation:
        return False

    listing_result = await db.execute(
        select(MarketplaceListing).where(MarketplaceListing.id == installation.listing_id)
    )
    listing = listing_result.scalar_one_or_none()

    if listing and listing.item_type == "mcp_tool":
        installed_tools_result = await db.execute(
            select(McpTool).where(
                McpTool.owner_id == user_id,
                McpTool.installed_from_listing_id == listing.id,
            )
        )
        installed_tools = list(installed_tools_result.scalars().all())
        for tool in installed_tools:
            await db.delete(tool)

    await db.delete(installation)
    await db.commit()
    logger.info(
        "Agent uninstalled",
        user_id=str(user_id),
        installation_id=str(installation_id),
    )
    return True


async def get_user_installations(
    db: AsyncSession, user_id: uuid.UUID
) -> list[UserAgentInstallation]:
    """Get all marketplace agents installed by the user."""
    result = await db.execute(
        select(UserAgentInstallation)
        .options(
            selectinload(UserAgentInstallation.listing).selectinload(
                MarketplaceListing.agent
            )
        )
        .where(UserAgentInstallation.user_id == user_id)
    )
    return list(result.scalars().all())


async def remove_listing(
    db: AsyncSession, publisher_id: uuid.UUID, listing_id: uuid.UUID
) -> bool:
    """Remove a marketplace listing owned by the publisher.

    Returns False when the listing does not exist or is not owned by the user.
    """
    result = await db.execute(
        select(MarketplaceListing).where(
            MarketplaceListing.id == listing_id,
            MarketplaceListing.publisher_id == publisher_id,
        )
    )
    listing = result.scalar_one_or_none()
    if not listing:
        return False

    await db.delete(listing)
    await db.commit()
    logger.info(
        "Marketplace listing removed",
        publisher_id=str(publisher_id),
        listing_id=str(listing_id),
    )
    return True
