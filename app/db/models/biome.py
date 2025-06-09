# --- START OF FILE app/db/models/biome.py ---

import uuid
from datetime import datetime
from typing import Optional, Dict, List, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, Float, Integer, JSON, func, Table, Column, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql as pg

from .base import Base

if TYPE_CHECKING:
    from .zone import Zone
    from .theme import ThemeDB

# Association table for many-to-many relationship between biomes and themes
biome_themes_association = Table(
    'biome_themes',
    Base.metadata,
    Column(
        'biome_id',
        pg.UUID(as_uuid=True),
        ForeignKey('biomes.id', ondelete='CASCADE'),
        primary_key=True,
        comment="Reference to biome"
    ),
    Column(
        'theme_id',
        pg.UUID(as_uuid=True),
        ForeignKey('themes.id', ondelete='CASCADE'),
        primary_key=True,
        comment="Reference to theme"
    ),
    Column(
        'created_at',
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When this biome-theme association was created"
    ),
    # Indexes for better query performance
    Index('idx_biome_themes_biome_id', 'biome_id'),
    Index('idx_biome_themes_theme_id', 'theme_id'),
    comment="Association table linking biomes to themes (many-to-many)"
)


class Biome(Base):
    """
    Database model representing biome types in the game world.
    Each biome affects movement, danger levels, and available resources.
    A biome can belong to multiple themes (e.g., "Forest" can be in both "Fantasy" and "Nature" themes).
    """
    __tablename__ = 'biomes'

    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    biome_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True,
                                          comment="Unique string identifier for the biome")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Display name of the biome")
    display_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="User-friendly display name")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Detailed description of the biome")

    # Gameplay attributes
    base_movement_modifier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0,
                                                          comment="Movement speed multiplier (1.0 = normal)")
    danger_level_base: Mapped[int] = mapped_column(Integer, nullable=False, default=1,
                                                   comment="Base danger level (1-5)")

    # Resource availability as JSON
    resource_types: Mapped[Optional[Dict[str, float]]] = mapped_column(
        JSON, nullable=True, default={},
        comment="Dictionary of resource types and their abundance multipliers"
    )

    # Visual representation
    color_hex: Mapped[Optional[str]] = mapped_column(String(10), nullable=True,
                                                     comment="Hexadecimal color code for map display")
    icon_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True,
                                                     comment="Path to biome icon image")

    # Standard timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(),
                                                           server_default=func.now())

    # RELATIONSHIPS

    # Many-to-many relationship with themes
    themes: Mapped[List["ThemeDB"]] = relationship(
        "ThemeDB",
        secondary=biome_themes_association,
        back_populates="biomes",
        lazy="select",
        cascade="",  # No cascade - let the association table handle deletions
    )

    # DEPRECATED - Relationship to zones
    # This relationship will be replaced by location_type relationships
    # in the new LocationInstance-based system
    zones: Mapped[List["Zone"]] = relationship(
        "Zone",
        back_populates="biome",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Biome(id={self.id!r}, biome_id={self.biome_id!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/biome.py ---