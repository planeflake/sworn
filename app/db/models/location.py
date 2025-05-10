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
# Import World model - no longer needed if World doesn't back-populate directly from here for characters
# from .world import World # This can cause circular dependency if World also imports Location
# TYPE CHECKING IMPORTS
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .character import Character
    from .world import World # Import for relationship type hint
    # from .item import Item # If items can be directly at locations

class Location(Base):
    """
    SQLAlchemy ORM Model for Locations.
    """
    __tablename__ = 'locations'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    world_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("worlds.id", name="fk_location_world_id", ondelete="CASCADE"), # Changed ondelete
        nullable=False,
        index=True
    )

    pos_x: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
    pos_y: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
    pos_z: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)

    # --- Relationships ---
    world: Mapped["World"] = relationship(
        "World",
        back_populates="locations" # Assumes World model has 'locations' relationship
    )

    characters_at_location: Mapped[List["Character"]] = relationship(
        "Character",
        foreign_keys="[Character.current_location_id]", # Explicitly use the Character's FK column
        back_populates="current_location",
        lazy="selectin"
    )

    # Optional: Relationship to Items directly at this location
    # items_at_location: Mapped[List["Item"]] = relationship(
    #     "Item",
    #     back_populates="location", # Assumes Item model will have 'location' relationship
    #     lazy="selectin"
    # )

    # --- Metadata (uncommented) ---
    _metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
       JSONB, nullable=True, default=lambda: {},
       comment="Data about the location, e.g., traversability, weather effects."
    )

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=True)

    # --- Table Args ---
    __table_args__ = (
        Index('ix_location_world_coords', 'world_id', 'pos_x', 'pos_y', 'pos_z', unique=False), # unique=True might be too restrictive
    )

    def __repr__(self) -> str:
        coords = f"({self.pos_x}, {self.pos_y}, {self.pos_z})" if self.pos_x is not None else ""
        return f"<Location(id={self.id!r}, name={self.name!r} {coords})>"

# --- END OF FILE app/db/models/location.py ---