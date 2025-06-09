# app/db/models/location_faction_presence.py

import uuid
from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from ..base import Base

class LocationFactionPresence(Base):
    __tablename__ = "location_faction_presence"

    # composite PK of (location_id, faction_id)
    location_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("location_entities.id",   ondelete="CASCADE"),
        primary_key=True,
    )
    faction_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("factions.id",            ondelete="CASCADE"),
        primary_key=True,
    )

    # percent presence from 0.0–100.0 (or 0.0–1.0)
    presence_pct: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Percentage of presence"
    )

    # relationships back to each parent
    location = relationship("LocationInstance", back_populates="present_factions")
    faction  = relationship("Faction",          back_populates="location_presences")
