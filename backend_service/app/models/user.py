"""User ORM model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    agents = relationship("Agent", back_populates="owner", lazy="selectin")
    mcp_tools = relationship("McpTool", back_populates="owner", lazy="selectin")
    sessions = relationship("UserSession", back_populates="user", lazy="selectin")
    marketplace_listings = relationship(
        "MarketplaceListing", back_populates="publisher", lazy="selectin"
    )
    installations = relationship(
        "UserAgentInstallation", back_populates="user", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"
