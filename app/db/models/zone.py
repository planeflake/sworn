import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import unique
import enum

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.sql import text

from .base import Base
from app.game_state.enums.shared import StatusEnum

@unique
class ZonalStateEnum(enum.Enum):
    PEACEFUL = "peaceful"
    HARMONIOUS = "harmonious"
    CHAOTIC = "chaotic"
    DESTROYED = "destroyed"
    UNDEFINED = "undefined"
    
    def __str__(self):
        return self.value

class Zone(Base):
    """
    Represents a geographical zone in the game world.
    Zones are areas that contain settlements, resources, and other game elements.
    They have specific biomes and themes that influence gameplay.
    """
    __tablename__ = 'zones'

    id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
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

    controlling_faction: Mapped[Optional[uuid.UUID]] = mapped_column(
        pg.UUID,
        nullable=True,
        default=None
    )

    state: Mapped[ZonalStateEnum] = mapped_column(
        SQLAlchemyEnum(ZonalStateEnum, name="zonal_state_enum"),
        nullable=False,
        default=ZonalStateEnum.PEACEFUL,
        index=True
    )

    status: Mapped[StatusEnum] = mapped_column(
        SQLAlchemyEnum(StatusEnum, name="status_enum", create_type=False),
        nullable=False,
        default=StatusEnum.ACTIVE,
        index=True
    )

    # Foreign keys
    world_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("worlds.id", name="fk_world_to_zone"),
        nullable=False
    )

    biome_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID,
        ForeignKey("biomes.id", name="fk_biome_to_zone"),
        nullable=False
    )

    # Timestamps
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

    # Additional data
    _metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        pg.JSONB,
        nullable=True,
        default=lambda: {}
    )

    tags: Mapped[Optional[List[str]]] = mapped_column(
        pg.ARRAY(String),
        nullable=True,
        default=lambda: []
    )

    # Relationships
    world = relationship("World")
    biome = relationship("Biome")
    settlements = relationship("Settlement")
    
    # For now, we'll skip the many-to-many relationship for generation purposes
    # We can add it back after the generator works
    # themes = relationship(
    #     "Theme",
    #     secondary="zone_theme_association",
    #     viewonly=True
    # )

    # Table arguments
    __table_args__ = (
        UniqueConstraint('name', 'world_id', name='uq_zone_name_world'),
    )

    def __repr__(self) -> str:
        return f"<Zone(id={self.id!r}, name={self.name!r})>"