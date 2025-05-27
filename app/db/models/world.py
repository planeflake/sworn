# --- START OF FILE app/db/models/world.py ---

import uuid # Import uuid for type hinting
from sqlalchemy import Integer, String, DateTime, func, ForeignKey, text # Added ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship # Added relationship
from sqlalchemy.dialects import postgresql as pg
from typing import List, Optional # Import List for relationship type hint
from datetime import datetime # Import datetime for type hinting
from .base import Base

# Import related models for TYPE_CHECKING block
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .location_instance import LocationInstance
    from .theme import ThemeDB # For theme relationship
    from .zone import Zone # For zones relationship - DEPRECATED

class World(Base):
    __tablename__ = 'worlds'

    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))

    theme_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("themes.id", name="fk_world_theme_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    theme: Mapped[Optional["ThemeDB"]] = relationship("ThemeDB", lazy="selectin")

    name: Mapped[str] = mapped_column(String(50), nullable=False, default="Default World", index=True)
    day: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    season: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Now we've added a migration for world_id in location_entities
    locations: Mapped[List["LocationInstance"]] = relationship(
        "LocationInstance",
        back_populates="world",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # DEPRECATED - For backward compatibility only
    # This relationship will be removed once transition to LocationInstance is complete
    zones: Mapped[List["Zone"]] = relationship(
        "Zone",
        back_populates="world",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<World(id={self.id!r}, name={self.name!r}, day={self.day}, season={self.season})>"


# --- END OF FILE app/db/models/world.py ---