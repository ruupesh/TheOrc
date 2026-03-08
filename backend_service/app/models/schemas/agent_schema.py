"""Pydantic schemas for Agent CRUD operations."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    """Request schema to register a new agent."""
    name: str = Field(max_length=255)
    description: str = Field(max_length=2000)
    host: str = Field(max_length=500)
    port: int = Field(ge=1, le=65535)
    agent_card_path: str = Field(default="/.well-known/agent.json", max_length=500)
    timeout: float = Field(default=300.0, ge=1.0)
    full_history: bool = True
    authentication_flag: bool = False
    allow_conversation_history: bool = True


class AgentUpdate(BaseModel):
    """Request schema to update an agent (all fields optional)."""
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    host: Optional[str] = Field(default=None, max_length=500)
    port: Optional[int] = Field(default=None, ge=1, le=65535)
    agent_card_path: Optional[str] = Field(default=None, max_length=500)
    timeout: Optional[float] = Field(default=None, ge=1.0)
    full_history: Optional[bool] = None
    authentication_flag: Optional[bool] = None
    allow_conversation_history: Optional[bool] = None


class AgentResponse(BaseModel):
    """Response schema for an agent."""
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    description: str
    host: str
    port: int
    agent_card_path: str
    timeout: float
    full_history: bool
    authentication_flag: bool
    allow_conversation_history: bool
    is_system: bool
    created_at: datetime

    model_config = {"from_attributes": True}
