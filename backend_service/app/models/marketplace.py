"""Marketplace ORM models — listings and user installations."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Either agent_id or mcp_tool_id must be set (not both)
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, unique=True
    )
    mcp_tool_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mcp_tools.id", ondelete="CASCADE"), nullable=True, unique=True
    )
    publisher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_type: Mapped[str] = mapped_column(String(20), nullable=False, default="agent")  # "agent" | "mcp_tool"
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="public")  # "public" | "private"
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String(5000), nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    agent = relationship("Agent", back_populates="marketplace_listing", lazy="selectin")
    mcp_tool = relationship(
        "McpTool",
        back_populates="marketplace_listing",
        foreign_keys=[mcp_tool_id],
        lazy="selectin",
    )
    publisher = relationship("User", back_populates="marketplace_listings")
    installations = relationship(
        "UserAgentInstallation", back_populates="listing", lazy="selectin"
    )

    @property
    def agent_card_url(self) -> str:
        """Derive agent card URL from the linked agent."""
        return self.agent.agent_card_url if self.agent else ""

    def __repr__(self) -> str:
        return f"<MarketplaceListing {self.title}>"


class UserAgentInstallation(Base):
    __tablename__ = "user_agent_installations"
    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", name="uq_user_listing"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("marketplace_listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    installed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="installations")
    listing = relationship("MarketplaceListing", back_populates="installations")

    def __repr__(self) -> str:
        return f"<UserAgentInstallation user={self.user_id} listing={self.listing_id}>"
