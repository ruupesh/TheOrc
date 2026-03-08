"""Agent ORM model — mirrors remote_agents_conf.yml fields, owned by a user."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    host: Mapped[str] = mapped_column(String(500), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_card_path: Mapped[str] = mapped_column(
        String(500), default="/.well-known/agent.json"
    )
    timeout: Mapped[float] = mapped_column(Float, default=300.0)
    full_history: Mapped[bool] = mapped_column(Boolean, default=True)
    authentication_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_conversation_history: Mapped[bool] = mapped_column(Boolean, default=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    owner = relationship("User", back_populates="agents")
    marketplace_listing = relationship(
        "MarketplaceListing", back_populates="agent", uselist=False, lazy="selectin"
    )

    @property
    def agent_card_url(self) -> str:
        """Build the full agent-card URL from host, port, and path."""
        base = f"{self.host.rstrip('/')}:{self.port}"
        return f"{base}{self.agent_card_path}"

    def __repr__(self) -> str:
        return f"<Agent {self.name} @ {self.host}:{self.port}>"
