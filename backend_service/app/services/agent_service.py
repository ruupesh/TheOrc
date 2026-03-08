"""Agent service — CRUD operations for user-owned agents."""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent
from app.models.marketplace import UserAgentInstallation, MarketplaceListing
from app.models.schemas.agent_schema import AgentCreate, AgentUpdate
from app.utils.logging import logger


async def create_agent(
    db: AsyncSession, owner_id: uuid.UUID, data: AgentCreate
) -> Agent:
    """Create a new agent owned by the user."""
    agent = Agent(owner_id=owner_id, **data.model_dump())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    logger.info("Agent created", agent_id=str(agent.id), name=agent.name)
    return agent


async def get_user_agents(
    db: AsyncSession, user_id: uuid.UUID, include_installed: bool = True
) -> list[Agent]:
    """Get all agents owned by the user, plus optionally installed marketplace agents."""
    # Own agents
    result = await db.execute(
        select(Agent).where(Agent.owner_id == user_id)
    )
    agents = list(result.scalars().all())

    # Installed marketplace agents
    if include_installed:
        result = await db.execute(
            select(Agent)
            .join(MarketplaceListing, MarketplaceListing.agent_id == Agent.id)
            .join(
                UserAgentInstallation,
                UserAgentInstallation.listing_id == MarketplaceListing.id,
            )
            .where(
                UserAgentInstallation.user_id == user_id,
                MarketplaceListing.is_published == True,
            )
        )
        installed_agents = list(result.scalars().all())
        # Avoid duplicates (user's own agents that are also published)
        existing_ids = {a.id for a in agents}
        for agent in installed_agents:
            if agent.id not in existing_ids:
                agents.append(agent)

    return agents


async def get_agent_by_id(
    db: AsyncSession, agent_id: uuid.UUID
) -> Optional[Agent]:
    """Get a single agent by ID."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    return result.scalar_one_or_none()


async def update_agent(
    db: AsyncSession, agent_id: uuid.UUID, owner_id: uuid.UUID, data: AgentUpdate
) -> Optional[Agent]:
    """Update an agent. Only the owner can update their own agents."""
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.owner_id == owner_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)
    logger.info("Agent updated", agent_id=str(agent_id))
    return agent


async def delete_agent(
    db: AsyncSession, agent_id: uuid.UUID, owner_id: uuid.UUID
) -> bool:
    """Delete an agent. Only the owner can delete their own non-system agents."""
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.owner_id == owner_id,
            Agent.is_system == False,
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        return False

    await db.delete(agent)
    await db.commit()
    logger.info("Agent deleted", agent_id=str(agent_id))
    return True
