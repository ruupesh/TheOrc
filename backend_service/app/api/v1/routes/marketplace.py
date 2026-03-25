"""Marketplace API routes — publish, browse, install, uninstall agents and MCP tools."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.schemas.marketplace_schema import (
    MarketplacePublishRequest,
    MarketplaceListingResponse,
    InstallAgentRequest,
    InstallationResponse,
)
from app.services import marketplace_service

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.post("/publish", response_model=MarketplaceListingResponse, status_code=status.HTTP_201_CREATED)
async def publish_item(
    data: MarketplacePublishRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MarketplaceListingResponse:
    """Publish one of your agents or MCP tools to the marketplace."""
    user_id = uuid.UUID(current_user["user_id"])
    try:
        listing = await marketplace_service.publish_item(
            db,
            publisher_id=user_id,
            title=data.title,
            description=data.description,
            visibility=data.visibility,
            agent_id=data.agent_id,
            mcp_tool_id=data.mcp_tool_id,
        )
        # Reload with relationships
        listing = await marketplace_service.get_listing_by_id(db, listing.id)
        return _build_listing_response(listing)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[MarketplaceListingResponse])
async def browse_marketplace(
    search: Optional[str] = Query(default=None, description="Search by title or description"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MarketplaceListingResponse]:
    """Browse all published items in the marketplace (public + own private)."""
    user_id = uuid.UUID(current_user["user_id"])
    listings = await marketplace_service.list_marketplace(
        db, current_user_id=user_id, search=search, skip=skip, limit=limit
    )
    return [_build_listing_response(listing) for listing in listings]


@router.get("/{listing_id}", response_model=MarketplaceListingResponse)
async def get_listing(
    listing_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MarketplaceListingResponse:
    """Get details of a marketplace listing."""
    listing = await marketplace_service.get_listing_by_id(db, listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return _build_listing_response(listing)


@router.post("/install", response_model=InstallationResponse, status_code=status.HTTP_201_CREATED)
async def install_agent(
    data: InstallAgentRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InstallationResponse:
    """Install a marketplace agent into your orchestrator."""
    user_id = uuid.UUID(current_user["user_id"])
    try:
        installation = await marketplace_service.install_agent(db, user_id, data.listing_id)
        return InstallationResponse(
            id=installation.id,
            user_id=installation.user_id,
            listing_id=installation.listing_id,
            installed_at=installation.installed_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/installations/me", response_model=list[InstallationResponse])
async def my_installations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[InstallationResponse]:
    """List all agents I have installed from the marketplace."""
    user_id = uuid.UUID(current_user["user_id"])
    installations = await marketplace_service.get_user_installations(db, user_id)
    return [
        InstallationResponse(
            id=inst.id,
            user_id=inst.user_id,
            listing_id=inst.listing_id,
            installed_at=inst.installed_at,
        )
        for inst in installations
    ]


@router.delete("/installations/{installation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def uninstall_agent(
    installation_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Uninstall a marketplace agent."""
    user_id = uuid.UUID(current_user["user_id"])
    removed = await marketplace_service.uninstall_agent(db, user_id, installation_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Installation not found or not owned by you",
        )


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_listing(
    listing_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove one of your own marketplace listings."""
    user_id = uuid.UUID(current_user["user_id"])
    removed = await marketplace_service.remove_listing(db, user_id, listing_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found or not owned by you",
        )


def _build_listing_response(listing) -> MarketplaceListingResponse:
    """Build a MarketplaceListingResponse from a MarketplaceListing ORM object."""
    return MarketplaceListingResponse(
        id=listing.id,
        agent_id=listing.agent_id,
        mcp_tool_id=listing.mcp_tool_id,
        publisher_id=listing.publisher_id,
        publisher_username=listing.publisher.username if listing.publisher else None,
        item_type=listing.item_type,
        visibility=listing.visibility,
        title=listing.title,
        description=listing.description,
        agent_card_url=listing.agent.agent_card_url if listing.agent else None,
        agent_name=listing.agent.name if listing.agent else None,
        agent_host=listing.agent.host if listing.agent else None,
        agent_port=listing.agent.port if listing.agent else None,
        mcp_tool_name=listing.mcp_tool.name if listing.mcp_tool else None,
        mcp_tool_connection_type=listing.mcp_tool.connection_type if listing.mcp_tool else None,
        is_published=listing.is_published,
        created_at=listing.created_at,
    )
