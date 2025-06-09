import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from sqlalchemy import (
    String, Text, Boolean,
    DateTime, Enum, func, ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.game_state.enums.shared import StatusEnum
from app.game_state.enums.resource import ResourceNodeVisibilityEnum

if TYPE_CHECKING:
    from app.db.models.resources.resource_node_link import ResourceNodeResource
    from app.db.models.location_instance import LocationInstance

class ResourceNode(Base):
    __tablename__ = "resource_nodes"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        unique=True
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    biome_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    depleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, name="resource_node_status_enum", create_type=False),
        nullable=False,
        default=StatusEnum.PENDING,
        index=True
    )

    visibility: Mapped[ResourceNodeVisibilityEnum] = mapped_column(
        Enum(ResourceNodeVisibilityEnum, name="resource_node_visibility_enum", create_type=False),
        nullable=False,
        default=ResourceNodeVisibilityEnum.HIDDEN,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=True
    )

    _metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict
    )

    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
        default=list
    )

    # Location relationship - links this node to a specific location
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("location_entities.id", name="fk_resource_node_location"),
        nullable=True,
        index=True
    )

    # One-to-many relationship to the edge model (ResourceNodeResource)
    resource_links: Mapped[List["ResourceNodeResource"]] = relationship(
        "ResourceNodeResource",
        back_populates="node",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Relationship to the location - use fully qualified string reference to avoid circular imports
    location: Mapped[Optional["LocationInstance"]] = relationship(
        "app.db.models.location_instance.LocationInstance",
        lazy="selectin",
        foreign_keys=[location_id]
    )

    def __repr__(self) -> str:
        return f"<ResourceNode(id={self.id}, name={self.name})>"