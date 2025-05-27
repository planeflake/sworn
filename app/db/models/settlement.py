# --- DEPRECATED FILE - DO NOT USE FOR NEW CODE ---
# Settlements should now be represented as LocationInstance objects with appropriate location_type.
#
# This file is kept temporarily for compatibility during transition.

from sqlalchemy import Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.dialects.postgresql import JSONB
from app.db.models.building_instance import BuildingInstanceDB
from sqlalchemy.sql import text
from .base import Base
import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

# Avoid circular imports by using TYPE_CHECKING
if TYPE_CHECKING:
    from .character import Character
    from .zone import Zone

class Settlement(Base):
    """
    DEPRECATED - Use LocationInstance with appropriate location_type instead.
    This model is kept only for backward compatibility during transition.
    """
    __tablename__ = 'settlements'

    # --- Fields REQUIRED in Python __init__ (Non-Defaults first) ---
    # Foreign Key to worlds table (No Python default, required)
    world_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("worlds.id"),
        nullable=False
        # init=True is default, so keep it in __init__
    )

    zone_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("zones.id",name="fk_settlement_zone_id"),
        nullable=False
    )

    # --- Fields OPTIONAL/PROVIDED in Python __init__ (Defaults available) ---
    # Primary Key (Has default, but you provide it)
    entity_id: Mapped[uuid.UUID] = mapped_column(
        "id",  # <<< Explicitly state the DB column name is "id"
        pg.UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        # init=True is default, keep it required for Python init
    )
    
    # Name (Has default, but you provide it)
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Default Settlement"
        # init=True is default, keep it in __init__
    )

    # --- Fields with defaults, EXCLUDED from Python __init__ ---
    # Population (Has default, you DON'T provide it -> init=False)
    population: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    # Resources (Has default, you DON'T provide it -> init=False)
    resources: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=lambda: {}
    )

    leader_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("characters.id"),
        nullable=True
    )

    # Relationship to the character who is the leader
    leader: Mapped[Optional["Character"]] = relationship(
        "Character",
        foreign_keys=[leader_id],
        lazy="selectin"
    )

    building_instances: Mapped[List["BuildingInstanceDB"]] = relationship(
        "BuildingInstanceDB",
        back_populates="settlement",
        cascade="all, delete-orphan"
    )

    # --- Timestamps (Already excluded from __init__) ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=True
    )


    # Relationship to the zone this settlement belongs to
    zone: Mapped["Zone"] = relationship(
        "Zone",
        back_populates="settlement_list",  # <- Must match the Zone model
        lazy="selectin"
    )