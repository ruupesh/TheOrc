"""MCP Tool service — CRUD operations for user-owned MCP tools."""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mcp_tool import McpTool
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
    db: AsyncSession, user_id: uuid.UUID
) -> list[McpTool]:
    """Get all MCP tools owned by the user."""
    result = await db.execute(
        select(McpTool).where(McpTool.owner_id == user_id)
    )
    return list(result.scalars().all())


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
