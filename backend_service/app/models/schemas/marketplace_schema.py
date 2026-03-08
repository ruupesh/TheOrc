"""Pydantic schemas for the Marketplace."""

import uuid
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class MarketplacePublishRequest(BaseModel):
    """Request to publish an agent or MCP tool to the marketplace."""
    agent_id: Optional[uuid.UUID] = None
    mcp_tool_id: Optional[uuid.UUID] = None
    title: str = Field(max_length=500)
    description: str = Field(max_length=5000)
    visibility: Literal["public", "private"] = "public"


class MarketplaceListingResponse(BaseModel):
    """Response schema for a marketplace listing."""
    id: uuid.UUID
    agent_id: Optional[uuid.UUID] = None
    mcp_tool_id: Optional[uuid.UUID] = None
    publisher_id: uuid.UUID
    publisher_username: Optional[str] = None
    item_type: str
    visibility: str
    title: str
    description: str
    # Agent fields (populated when item_type == "agent")
    agent_card_url: Optional[str] = None
    agent_name: Optional[str] = None
    agent_host: Optional[str] = None
    agent_port: Optional[int] = None
    # MCP tool fields (populated when item_type == "mcp_tool")
    mcp_tool_name: Optional[str] = None
    mcp_tool_connection_type: Optional[str] = None
    is_published: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class InstallAgentRequest(BaseModel):
    """Request to install an agent from the marketplace."""
    listing_id: uuid.UUID


class InstallationResponse(BaseModel):
    """Response for an agent installation."""
    id: uuid.UUID
    user_id: uuid.UUID
    listing_id: uuid.UUID
    installed_at: datetime
    listing: Optional[MarketplaceListingResponse] = None

    model_config = {"from_attributes": True}
