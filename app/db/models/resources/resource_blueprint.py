# --- START - app/db/models/resources/resource_blueprint.py ---

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List

# Core SQLAlchemy imports
from sqlalchemy import (
    Integer, String, DateTime, func, Enum, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import text
from sqlalchemy import ForeignKey
from app.db.models.base import Base
from app.game_state.enums.shared import RarityEnum, StatusEnum

if TYPE_CHECKING:
    from app.db.models.resources.resource_node_blueprint_link import ResourceNodeBlueprintResource
    from app.db.models.resources.resource_node_link import ResourceNodeResource
    from app.db.models.resources.resource_instance import ResourceInstance

class ResourceBlueprint(Base):
    """
    SQLAlchemy ORM Model for Resource Types.
    """
    __tablename__ = 'resources'
    __table_args__ = {'extend_existing': True}

    resource_id: Mapped[uuid.UUID] = mapped_column(
        "id",
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    rarity: Mapped[Optional[RarityEnum]] = mapped_column(
        Enum(RarityEnum, name="rarity_enum", create_type=False),
        nullable=True,
        default=RarityEnum.COMMON,
        index=True
    )

    stack_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
        server_default='100'
    )

    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, name="status_enum", create_type=False),
        nullable=False,
        default=StatusEnum.ACTIVE,
        server_default=StatusEnum.ACTIVE.value,
        index=True
    )

    theme_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("themes.id"),
        nullable=False
    )

    blueprint_links: Mapped[List["ResourceNodeBlueprintResource"]] = relationship(
        "ResourceNodeBlueprintResource",
        back_populates="resource",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Added relationship to ResourceNodeResource (ResourceNodeLink)
    node_links: Mapped[List["ResourceNodeResource"]] = relationship(
        "ResourceNodeResource",
        back_populates="resource",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    instances: Mapped[List["ResourceInstance"]] = relationship(
        "ResourceInstance",
        back_populates="resource",
        cascade="all, delete-orphan",
        lazy="selectin"
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
    
    def __repr__(self) -> str:
        return f"<Resource(id={self.resource_id}, name={self.name})>"

# --- END - app/db/models/resources/resource_blueprint.py ---