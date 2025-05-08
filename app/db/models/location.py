# --- START OF FILE app/db/models/location.py ---

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Integer, String, Text, DateTime, func, ForeignKey, Float, Index, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB

from .base import Base
from .world import World # Import the World model
from sqlalchemy.sql import text
# Import Character only needed for type hinting if using TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .character import Character
    # from .item import Item # If items can be directly at locations

class Location(Base):
    """
    SQLAlchemy ORM Model for Locations.
    Represents a specific place, area, or coordinate within a World.
    Could be a region, building interior, specific map coordinate, etc.
    """
    __tablename__ = 'locations'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Foreign Key to the World this location is in
    world_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("worlds.id", name="fk_location_world_id"),
        nullable=False,
        index=True
    )

    # Optional coordinates or area definition
    pos_x: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
    pos_y: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
    pos_z: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
    # area_bounds: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True) # e.g., for polygon area

    # --- Relationships ---
    # Relationship back to the World
    world: Mapped["World"] = relationship(
        "World",
        back_populates="locations" # Assumes World model has 'locations' relationship
    )

    # Relationship to Characters currently at this location
    # Matches 'current_location' in Character model
    characters_at_location: Mapped[List["Character"]] = relationship(
        "Character",
        back_populates="current_location",
        lazy="selectin" # Load characters when location is loaded
    )

    # Optional: Relationship to Items directly at this location (on the ground)
    # items_at_location: Mapped[List["Item"]] = relationship(
    #     "Item",
    #     back_populates="location",
    #     lazy="selectin"
    # )

    # --- Metadata ---
    #etadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
    #    JSONB, nullable=True, default=lambda: {},
    #    comment="Data about the location, e.g., traversability, weather effects."
    #)

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # --- Table Args ---
    __table_args__ = (
        Index('ix_location_world_coords', 'world_id', 'pos_x', 'pos_y', 'pos_z', unique=True), # Example index
    )

    def __repr__(self) -> str:
        coords = f"({self.pos_x}, {self.pos_y}, {self.pos_z})" if self.pos_x is not None else ""
        return f"<Location(id={self.id!r}, name={self.name!r} {coords})>"

# --- END OF FILE app/db/models/location.py ---