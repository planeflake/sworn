import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from app.game_state.enums.shared import StatusEnum

from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    Date,
    Enum,
    ForeignKey,
    func
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import text

from app.db.models.locations.location_faction_presence import LocationFactionPresence
from .base import Base

class Faction(Base):
    __tablename__ = 'factions'

    id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, name="status_enum", create_type=False),
        nullable=False,
        default=StatusEnum.PENDING,
        index=True
    )

    icon_path: Mapped[str] = mapped_column(String, nullable=False, default="")
    member_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    leader_last_changed: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    theme: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("themes.id", name="faction_theme_id"),
        nullable=True
    )

    location_presences: Mapped[list[LocationFactionPresence]] = relationship(
        "LocationFactionPresence",
        back_populates="faction",
        lazy="selectin",
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=True)

    _metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True, default=lambda: {})
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True, default=lambda: [])

    # DEPRECATED - One faction controls many zones
    # This relationship will be replaced by location-based faction control
    # in the new LocationInstance-based system
    zones = relationship("Zone", back_populates="faction", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id!r}, name={self.name!r})>"
