# --- START OF FILE app/db/models/world.py ---

import uuid # Import uuid for type hinting
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, text # Added ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship # Added relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID # Use pgUUID for clarity
from typing import List, Optional # Import List for relationship type hint
from datetime import datetime # Import datetime for type hinting


from app.db.models.character import Character # Import Character model for relationship
from .base import Base
# Import related models for TYPE_CHECKING block
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .location import Location
    from .theme import Theme # For theme relationship

class World(Base):
    """World model for SQLAlchemy ORM"""
    __tablename__ = 'worlds'

    id: Mapped[uuid.UUID] = mapped_column( # Use uuid.UUID for Mapped type hint
        pgUUID(as_uuid=True), # Store as native PG UUID, use Python UUID objects
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # --- Foreign Key and Relationship to Theme ---
    theme_id: Mapped[Optional[uuid.UUID]] = mapped_column( # Use uuid.UUID, made Optional for now
        pgUUID(as_uuid=True),
        ForeignKey("themes.id", name="fk_world_theme_id", ondelete="SET NULL"), # Link to themes table
        nullable=True, # Can a world exist without a theme initially? If not, set to False
        index=True
    )
    theme: Mapped[Optional["Theme"]] = relationship( # Optional if theme_id is nullable
        "Theme",
        # back_populates="worlds" # Assumes Theme model will have a 'worlds' relationship
        lazy="selectin"
    )

    name: Mapped[str] = mapped_column(String(50), nullable=False, default="Default World", index=True) # Added index
    day: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0') # Added server_default
    season: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0') # Added server_default
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0') # Added server_default

    # `settlements` would typically be a relationship to a Settlement model, not a string column.
    # Example:
    # settlements: Mapped[List["Settlement"]] = relationship("Settlement", back_populates="world", cascade="all, delete-orphan")
    # If you are storing a list of settlement IDs or names as a simple list, use ARRAY:
    # settlement_names: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False # Added timezone=True
    )
    updated_at: Mapped[datetime] = mapped_column( # Usually should be Optional or have init=False if fully DB managed
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False # Added timezone=True
    )

    # --- Relationship to Locations ---
    # One World can have many Locations
    locations: Mapped[List["Location"]] = relationship(
        "Location",
        back_populates="world", # Matches 'world' relationship in Location model
        cascade="all, delete-orphan", # If deleting world deletes its locations
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<World(id={self.id!r}, name={self.name!r}, day={self.day}, season={self.season})>"

    # __eq__ is often not needed for ORM models if relying on PK for identity.
    # SQLAlchemy handles identity tracking. If you need it for specific comparisons:
    # def __eq__(self, other: object) -> bool:
    #     if not isinstance(other, World):
    #         return NotImplemented
    #     # Compare by ID if available and persistent
    #     if self.id is not None and other.id is not None:
    #         return self.id == other.id
    #     # Fallback to attribute comparison if IDs are not set (transient objects)
    #     return (self.name == other.name and
    #             self.day == other.day and
    #             self.season == other.season and
    #             self.theme_id == other.theme_id) # Consider all identifying attributes

    # `__to_dict__` is also often not needed as Pydantic schemas handle serialization.
    # If needed for very simple cases:
    # def to_dict(self) -> dict:
    #     return {
    #         "id": str(self.id) if self.id else None,
    #         "name": self.name,
    #         "day": self.day,
    #         "season": self.season,
    #         "theme_id": str(self.theme_id) if self.theme_id else None,
    #         "created_at": self.created_at.isoformat() if self.created_at else None,
    #         "updated_at": self.updated_at.isoformat() if self.updated_at else None
    #     }

# --- END OF FILE app/db/models/world.py ---