# --- FILE: app/db/models/travel_link.py ---

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Float, Integer, Boolean, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.dialects.postgresql import ARRAY

from .base import Base

if TYPE_CHECKING:
    from .location_instance import LocationInstance
    from .biome import Biome
    from .faction import Faction

class TravelLink(Base):
    """
    SQLAlchemy ORM Model for Travel Links between locations.
    Defines connections and travel parameters between different locations.
    """
    __tablename__ = "travel_links"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="Name of the travel route")
    
    # Source and destination locations
    from_location_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("location_entities.id", name="fk_travel_from_location", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    to_location_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("location_entities.id", name="fk_travel_to_location", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Travel parameters
    speed: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0,
        comment="Speed multiplier for travel (1.0 = normal speed)"
    )
    
    path_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="trail",
        comment="Type of path (road, trail, forest path, etc.)"
    )
    
    terrain_modifier: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0,
        comment="Terrain difficulty modifier (0.5 = easier, 2.0 = harder)"
    )
    
    base_danger_level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1,
        comment="Base danger level for this route (1-10)"
    )
    
    # Distance and time
    distance_km: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Distance in kilometers"
    )
    
    base_travel_time_hours: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True,
        comment="Base travel time in hours"
    )
    
    # Visibility and accessibility
    visibility: Mapped[str] = mapped_column(
        String(20), nullable=False, default="visible",
        comment="Visibility status: visible, hidden, secret"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True,
        comment="Whether this travel link is currently usable"
    )
    
    # Environmental conditions
    weather_affected: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True,
        comment="Whether weather affects travel on this route"
    )
    
    seasonal_modifiers: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        pg.JSONB, nullable=True,
        comment="Seasonal travel modifiers (JSON object)"
    )
    
    # Biomes encountered during travel
    biome_ids: Mapped[Optional[List[uuid.UUID]]] = mapped_column(
        ARRAY(pg.UUID(as_uuid=True)), nullable=True,
        comment="Biomes encountered during travel"
    )
    
    # Factions with influence along this route
    faction_ids: Mapped[Optional[List[uuid.UUID]]] = mapped_column(
        ARRAY(pg.UUID(as_uuid=True)), nullable=True,
        comment="Factions with influence along this route"
    )
    
    # Additional metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # --- Relationships ---
    from_location: Mapped["LocationInstance"] = relationship(
        "LocationInstance",
        foreign_keys=[from_location_id],
        back_populates="outgoing_travel_links",
        lazy="selectin"
    )
    
    to_location: Mapped["LocationInstance"] = relationship(
        "LocationInstance",
        foreign_keys=[to_location_id],
        back_populates="incoming_travel_links",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<TravelLink(id={self.id!r}, name={self.name!r}, from={self.from_location_id}, to={self.to_location_id})>"