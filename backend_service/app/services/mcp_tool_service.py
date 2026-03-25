"""MCP Tool service — CRUD operations for user-owned MCP tools."""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mcp_tool import McpTool
from app.models.marketplace import MarketplaceListing
from app.models.schemas.mcp_tool_schema import McpToolCreate, McpToolUpdate
from app.utils.logging import logger


async def create_mcp_tool(
    db: AsyncSession, owner_id: uuid.UUID, data: McpToolCreate
) -> McpTool:
    """Create a new MCP tool owned by the user."""
    tool = McpTool(owner_id=owner_id, **data.model_dump())
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    logger.info("MCP tool created", tool_id=str(tool.id), name=tool.name)
    return tool


async def get_user_mcp_tools(
    db: AsyncSession, user_id: uuid.UUID, include_installed: bool = True
) -> list[McpTool]:
    """Get MCP tools accessible to the user.

    Includes:
    - user-owned MCP tools
    - MCP tools from listings published by the current user
    - installed marketplace MCP tools are represented as user-owned cloned tools
    """
    result = await db.execute(
        select(McpTool).where(McpTool.owner_id == user_id)
    )
    tools = list(result.scalars().all())

    # Include MCP tools from listings published by this user.
    # This handles datasets where listing publisher and tool owner may differ.
    result = await db.execute(
        select(McpTool)
        .join(MarketplaceListing, MarketplaceListing.mcp_tool_id == McpTool.id)
        .where(
            MarketplaceListing.publisher_id == user_id,
            MarketplaceListing.mcp_tool_id.is_not(None),
            MarketplaceListing.is_published == True,
        )
    )
    published_tools = list(result.scalars().all())
    existing_ids = {t.id for t in tools}
    for tool in published_tools:
        if tool.id not in existing_ids:
            tools.append(tool)
            existing_ids.add(tool.id)

    if not include_installed:
        tools = [t for t in tools if t.installed_from_listing_id is None]

    return tools


async def get_user_mcp_tool_by_id(
    db: AsyncSession, user_id: uuid.UUID, tool_id: uuid.UUID
) -> Optional[McpTool]:
    """Get a single MCP tool by ID only if it is accessible to the user."""
    result = await db.execute(
        select(McpTool).where(McpTool.id == tool_id, McpTool.owner_id == user_id)
    )
    tool = result.scalar_one_or_none()
    if tool:
        return tool

    # Backward compatibility: allow reading tools from listings published by this user
    result = await db.execute(
        select(McpTool)
        .join(MarketplaceListing, MarketplaceListing.mcp_tool_id == McpTool.id)
        .where(
            McpTool.id == tool_id,
            MarketplaceListing.publisher_id == user_id,
            MarketplaceListing.is_published == True,
        )
    )
    return result.scalar_one_or_none()


async def get_mcp_tool_by_id(
    db: AsyncSession, tool_id: uuid.UUID
) -> Optional[McpTool]:
    """Get a single MCP tool by ID."""
    result = await db.execute(select(McpTool).where(McpTool.id == tool_id))
    return result.scalar_one_or_none()


async def update_mcp_tool(
    db: AsyncSession, tool_id: uuid.UUID, owner_id: uuid.UUID, data: McpToolUpdate
) -> Optional[McpTool]:
    """Update an MCP tool. Only the owner can update their own tools."""
    result = await db.execute(
        select(McpTool).where(McpTool.id == tool_id, McpTool.owner_id == owner_id)
    )
    tool = result.scalar_one_or_none()
    if not tool:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tool, field, value)

    await db.commit()
    await db.refresh(tool)
    logger.info("MCP tool updated", tool_id=str(tool_id))
    return tool


async def delete_mcp_tool(
    db: AsyncSession, tool_id: uuid.UUID, owner_id: uuid.UUID
) -> bool:
    """Delete an MCP tool. Only the owner can delete their own non-system tools."""
    result = await db.execute(
        select(McpTool).where(
            McpTool.id == tool_id,
            McpTool.owner_id == owner_id,
            McpTool.is_system == False,
        )
    )
    tool = result.scalar_one_or_none()
    if not tool:
        return False

    await db.delete(tool)
    await db.commit()
    logger.info("MCP tool deleted", tool_id=str(tool_id))
    return True
