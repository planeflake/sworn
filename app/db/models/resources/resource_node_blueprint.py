from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from sqlalchemy import (
    String, Text, Boolean,
    DateTime, Enum, func
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.game_state.enums.shared import StatusEnum
from app.db.models.resources.resource_node_blueprint_link import ResourceNodeBlueprintResource

# Avoid circular import errors during runtime
if TYPE_CHECKING:
    from app.db.models.resources.resource_node_link import ResourceNodeResource


class ResourceNodeBlueprint(Base):
    """
    SQLAlchemy ORM Model for Resource Node Blueprints.
    These are templates that can be used to generate resource node instances.
    """
    __tablename__ = "resource_node_blueprints"

    id: Mapped[UUID] = mapped_column(
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

    resource_links: Mapped[List["ResourceNodeBlueprintResource"]] = relationship(
        "ResourceNodeBlueprintResource",
        back_populates="blueprint",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ResourceNode(id={self.id}, name={self.name})>"
