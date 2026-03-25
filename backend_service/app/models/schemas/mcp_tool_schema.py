"""Pydantic schemas for MCP Tool CRUD operations."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class McpToolCreate(BaseModel):
    """Request schema to register a new MCP tool."""
    name: str = Field(max_length=255)
    connection_type: str = Field(max_length=50)  # stdio | streamable_http | sse

    # Stdio-specific
    command: Optional[str] = Field(default=None, max_length=255)
    args: Optional[list[str]] = None
    env: Optional[dict[str, str]] = None

    # HTTP/SSE-specific
    url: Optional[str] = Field(default=None, max_length=1000)
    headers: Optional[dict[str, str]] = None
    sse_read_timeout: float = 300.0

    # Common
    timeout: float = Field(default=30.0, ge=1.0)
    authentication_flag: bool = False
    auth_token: Optional[str] = None
    tool_filter: Optional[list[str]] = None


class McpToolUpdate(BaseModel):
    """Request schema to update an MCP tool (all fields optional)."""
    name: Optional[str] = Field(default=None, max_length=255)
    connection_type: Optional[str] = Field(default=None, max_length=50)
    command: Optional[str] = Field(default=None, max_length=255)
    args: Optional[list[str]] = None
    env: Optional[dict[str, str]] = None
    url: Optional[str] = Field(default=None, max_length=1000)
    headers: Optional[dict[str, str]] = None
    sse_read_timeout: Optional[float] = None
    timeout: Optional[float] = Field(default=None, ge=1.0)
    authentication_flag: Optional[bool] = None
    auth_token: Optional[str] = None
    tool_filter: Optional[list[str]] = None


class McpToolResponse(BaseModel):
    """Response schema for an MCP tool."""
    id: uuid.UUID
    owner_id: uuid.UUID
    installed_from_listing_id: Optional[uuid.UUID] = None
    name: str
    connection_type: str
    command: Optional[str] = None
    args: Optional[list] = None
    env: Optional[dict] = None
    url: Optional[str] = None
    headers: Optional[dict] = None
    sse_read_timeout: float
    timeout: float
    authentication_flag: bool
    tool_filter: Optional[list] = None
    is_system: bool
    created_at: datetime

    model_config = {"from_attributes": True}
