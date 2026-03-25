"""MCP Tool management API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.schemas.mcp_tool_schema import McpToolCreate, McpToolUpdate, McpToolResponse
from app.services import mcp_tool_service

router = APIRouter(prefix="/mcp-tools", tags=["MCP Tools"])


@router.get("", response_model=list[McpToolResponse])
async def list_mcp_tools(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[McpToolResponse]:
    """List MCP tools accessible to the current user (own + published by me + installed)."""
    user_id = uuid.UUID(current_user["user_id"])
    tools = await mcp_tool_service.get_user_mcp_tools(db, user_id)
    return [McpToolResponse.model_validate(t) for t in tools]


@router.post("", response_model=McpToolResponse, status_code=status.HTTP_201_CREATED)
async def create_mcp_tool(
    data: McpToolCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> McpToolResponse:
    """Register a new MCP tool."""
    user_id = uuid.UUID(current_user["user_id"])
    tool = await mcp_tool_service.create_mcp_tool(db, user_id, data)
    return McpToolResponse.model_validate(tool)


@router.get("/{tool_id}", response_model=McpToolResponse)
async def get_mcp_tool(
    tool_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> McpToolResponse:
    """Get MCP tool details by ID."""
    user_id = uuid.UUID(current_user["user_id"])
    tool = await mcp_tool_service.get_user_mcp_tool_by_id(db, user_id, tool_id)
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP tool not found")
    return McpToolResponse.model_validate(tool)


@router.put("/{tool_id}", response_model=McpToolResponse)
async def update_mcp_tool(
    tool_id: uuid.UUID,
    data: McpToolUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> McpToolResponse:
    """Update an MCP tool (only own tools)."""
    user_id = uuid.UUID(current_user["user_id"])
    tool = await mcp_tool_service.update_mcp_tool(db, tool_id, user_id, data)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP tool not found or you don't have permission to update it",
        )
    return McpToolResponse.model_validate(tool)


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp_tool(
    tool_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an MCP tool (only own non-system tools)."""
    user_id = uuid.UUID(current_user["user_id"])
    deleted = await mcp_tool_service.delete_mcp_tool(db, tool_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCP tool not found, not owned by you, or is a system tool",
        )
