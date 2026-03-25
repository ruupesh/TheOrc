"""McpTool ORM model — mirrors mcp_conf.yml fields, owned by a user."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class McpTool(Base):
    __tablename__ = "mcp_tools"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    installed_from_listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("marketplace_listings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    connection_type: Mapped[str] = mapped_column(String(50), nullable=False)  # stdio | streamable_http | sse

    # Stdio-specific
    command: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    args: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    env: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # HTTP/SSE-specific
    url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    headers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    sse_read_timeout: Mapped[float] = mapped_column(Float, default=300.0)

    # Common
    timeout: Mapped[float] = mapped_column(Float, default=30.0)
    authentication_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    auth_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tool_filter: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    owner = relationship("User", back_populates="mcp_tools")
    marketplace_listing = relationship(
        "MarketplaceListing",
        back_populates="mcp_tool",
        foreign_keys="MarketplaceListing.mcp_tool_id",
        uselist=False,
        lazy="selectin",
    )
    installed_from_listing = relationship(
        "MarketplaceListing",
        foreign_keys=[installed_from_listing_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<McpTool {self.name} ({self.connection_type})>"
