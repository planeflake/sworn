# --- START OF FILE app/db/models/theme.py ---

import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql as pg

from app.db.models.tool_tier import ToolTier
from .base import Base
from app.db.models.biome import Biome

from app.game_state.enums.theme import Genre

if TYPE_CHECKING:
    from app.db.models.location_sub_type import LocationSubType

class ThemeDB(Base):
    __tablename__ = 'themes'

    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    genre: Mapped[Optional[Genre]] = mapped_column(SQLEnum(Genre), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships

    # Many-to-many relationship with biomes
    biomes: Mapped[List["Biome"]] = relationship(
        "Biome",
        secondary="biome_themes",  # Reference by table name
        back_populates="themes",
        lazy="select",
        cascade=""
    )

    location_sub_types: Mapped[List["LocationSubType"]] = relationship(
        "LocationSubType",
        back_populates="theme",
        cascade="all, delete-orphan"
    )

    tool_tiers: Mapped[list["ToolTier"]] = relationship("ToolTier", back_populates="theme")

    def __repr__(self) -> str:
        return f"<ThemeDB(id={self.id!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/theme.py ---
