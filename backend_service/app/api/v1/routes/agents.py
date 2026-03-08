"""Agent management API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.schemas.agent_schema import AgentCreate, AgentUpdate, AgentResponse
from app.services import agent_service

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AgentResponse]:
    """List all agents accessible to the current user (own + installed from marketplace)."""
    user_id = uuid.UUID(current_user["user_id"])
    agents = await agent_service.get_user_agents(db, user_id)
    return [AgentResponse.model_validate(a) for a in agents]


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    data: AgentCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AgentResponse:
    """Register a new agent."""
    user_id = uuid.UUID(current_user["user_id"])
    agent = await agent_service.create_agent(db, user_id, data)
    return AgentResponse.model_validate(agent)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AgentResponse:
    """Get agent details by ID."""
    agent = await agent_service.get_agent_by_id(db, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return AgentResponse.model_validate(agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: uuid.UUID,
    data: AgentUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AgentResponse:
    """Update an agent (only own agents)."""
    user_id = uuid.UUID(current_user["user_id"])
    agent = await agent_service.update_agent(db, agent_id, user_id, data)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or you don't have permission to update it",
        )
    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an agent (only own non-system agents)."""
    user_id = uuid.UUID(current_user["user_id"])
    deleted = await agent_service.delete_agent(db, agent_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found, not owned by you, or is a system agent",
        )
