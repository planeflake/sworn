# --- DEPRECATED FILE - DO NOT USE FOR NEW CODE ---
# Zones should now be represented as LocationInstance objects with appropriate location_type.
#
# This file is kept temporarily for compatibility during transition.

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

# Import needed for compatibility - NOT FOR NEW CODE
from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.sql import text

from .base import Base
from app.game_state.enums.shared import StatusEnum

# Define as class but mark as deprecated
class Zone(Base):
    """
    DEPRECATED - Use LocationInstance with appropriate location_type instead.
    This model is kept only for backward compatibility during transition.
    """
    __tablename__ = 'zones'

    id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    controlling_faction: Mapped[Optional[uuid.UUID]] = mapped_column(
        pg.UUID,
        ForeignKey("factions.id", name="fk_faction_to_zone"),
        nullable=True,
        default=None
    )

    status: Mapped[StatusEnum] = mapped_column(
        SQLAlchemyEnum(StatusEnum, name="status_enum", create_type=False),
        nullable=False,
        default=StatusEnum.ACTIVE,
        index=True
    )

    world_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID,
        ForeignKey("worlds.id", name="fk_world_to_zone"),
        nullable=False
    )

    biome_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID,
        ForeignKey("biomes.id", name="fk_biome_to_zone"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=True)

    _metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(pg.JSONB, nullable=True, default=lambda: {})
    tags: Mapped[Optional[List[str]]] = mapped_column(pg.ARRAY(String), nullable=True, default=lambda: [])

    # Add the relationship to World
    world = relationship("World", back_populates="zones")
    biome = relationship("Biome", back_populates="zones")
    settlement_list = relationship("Settlement", back_populates="zone", cascade="all, delete-orphan")

    # This is a many-to-one relationship: each zone is controlled by one faction
    faction = relationship("Faction", back_populates="zones", foreign_keys=[controlling_faction])

    __table_args__ = (
        UniqueConstraint('name', 'world_id', name='uq_zone_name_world'),
    )