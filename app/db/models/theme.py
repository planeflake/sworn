# --- START OF FILE app/db/models/theme.py ---

import uuid # Import uuid for type hinting Mapped[uuid.UUID]
from sqlalchemy import Column, String, Text, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship # Added relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID # Renamed to pgUUID for clarity
from sqlalchemy.sql import text
from typing import Optional, List # Added List for relationship
from .base import Base
from datetime import datetime

# Import related models for type hinting within TYPE_CHECKING block
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .building_blueprint import BuildingBlueprint # For the relationship

class Theme(Base):
    """Theme model for SQLAlchemy ORM"""
    __tablename__ = 'themes'

    id: Mapped[uuid.UUID] = mapped_column( # Changed from UUID to uuid.UUID for consistency
        pgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True) # Added index
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False # Added timezone=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False # Added timezone=True
    )

    # --- Relationship to BuildingBlueprints ---
    # One Theme can have many BuildingBlueprints
    building_blueprints: Mapped[List["BuildingBlueprint"]] = relationship(
        "BuildingBlueprint",
        back_populates="theme", # Matches 'theme' relationship in BuildingBlueprint
        cascade="all, delete-orphan", # Optional: if deleting a theme deletes its blueprints
        lazy="selectin"
    )

    # Add other columns corresponding to the entity

    def __repr__(self) -> str:
        return f"<Theme(id={self.id!r}, name='{self.name!r}')>" # Used !r for id and name

# --- END OF FILE app/db/models/theme.py ---