# app/db/models/resources/resource_instance.py

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.resources.resource_blueprint import ResourceBlueprint

class ResourceInstance(Base):
    __tablename__ = "resource_instances"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    location_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("location_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    resource_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False
    )

    resource: Mapped["ResourceBlueprint"] = relationship(
        "ResourceBlueprint",
        back_populates="instances",
        lazy="selectin"
    )

    resource_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True
    )

    owner_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True  # e.g., 'character', 'settlement', 'world'
    )

    _metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<ResourceInstance(id={self.id}, resource={self.resource_id}, count={self.resource_count}, owner={self.owner_type}:{self.owner_id})>"
