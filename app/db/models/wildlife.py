# --- FILE: app/db/models/wildlife.py ---

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum

from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime, func, Text, Float, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from .base import Base

if TYPE_CHECKING:
    from .location_instance import LocationInstance
    from .biome import Biome

class WildlifeTypeEnum(Enum):
    """Types of wildlife that can inhabit areas."""
    HERBIVORE = "herbivore"
    CARNIVORE = "carnivore"
    OMNIVORE = "omnivore"
    MAGICAL_CREATURE = "magical_creature"
    BANDIT = "bandit"
    MONSTER = "monster"
    UNDEAD = "undead"
    ELEMENTAL = "elemental"

class WildlifeThreatLevelEnum(Enum):
    """Threat level classifications for wildlife."""
    HARMLESS = "harmless"
    PASSIVE = "passive"
    DEFENSIVE = "defensive"
    AGGRESSIVE = "aggressive"
    HOSTILE = "hostile"
    DEADLY = "deadly"

class Wildlife(Base):
    """
    SQLAlchemy ORM Model for Wildlife/Creatures that inhabit locations.
    These affect travel danger and location characteristics.
    """
    __tablename__ = "wildlife"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Classification
    wildlife_type: Mapped[WildlifeTypeEnum] = mapped_column(
        SQLAlchemyEnum(WildlifeTypeEnum, name="wildlife_type_enum", create_type=False),
        nullable=False, index=True
    )
    
    threat_level: Mapped[WildlifeThreatLevelEnum] = mapped_column(
        SQLAlchemyEnum(WildlifeThreatLevelEnum, name="wildlife_threat_level_enum", create_type=False),
        nullable=False, index=True
    )
    
    # Location reference
    location_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("location_entities.id", name="fk_wildlife_location", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Population and spawn data
    population: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1,
        comment="Current population in this location"
    )
    
    max_population: Mapped[int] = mapped_column(
        Integer, nullable=False, default=10,
        comment="Maximum sustainable population"
    )
    
    spawn_rate: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.1,
        comment="Daily spawn rate (0.0 to 1.0)"
    )
    
    # Danger and combat stats
    danger_rating: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1,
        comment="Individual danger rating (1-10)"
    )
    
    pack_behavior: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Whether creatures group together for increased danger"
    )
    
    pack_size_min: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1,
        comment="Minimum pack size"
    )
    
    pack_size_max: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1,
        comment="Maximum pack size"
    )
    
    # Behavior and traits
    territorial: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Whether creatures defend territory aggressively"
    )
    
    nocturnal: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Whether creatures are more active at night"
    )
    
    seasonal_activity: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
        comment="Seasonal activity modifiers"
    )
    
    # Preferred biomes
    preferred_biome_ids: Mapped[Optional[List[uuid.UUID]]] = mapped_column(
        ARRAY(pg.UUID(as_uuid=True)), nullable=True,
        comment="Biomes where this wildlife thrives"
    )
    
    # Loot and resources
    drops_resources: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Whether defeating this wildlife drops resources"
    )
    
    resource_drops: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, nullable=True,
        comment="Resources that can be obtained from this wildlife"
    )
    
    # Activity status
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True,
        comment="Whether this wildlife is currently active in the location"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_spawn: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    location: Mapped["LocationInstance"] = relationship(
        "LocationInstance",
        back_populates="wildlife",
        lazy="selectin"
    )

    def get_effective_danger(self) -> int:
        """Calculate effective danger based on population and pack behavior."""
        base_danger = self.danger_rating * self.population
        
        if self.pack_behavior and self.population >= self.pack_size_min:
            # Pack bonus increases danger
            pack_bonus = min(self.population // self.pack_size_min, 3) * 0.5
            return int(base_danger * (1 + pack_bonus))
        
        return base_danger

    def __repr__(self):
        return f"<Wildlife(id={self.id!r}, name={self.name!r}, type={self.wildlife_type.value}, threat={self.threat_level.value})>"