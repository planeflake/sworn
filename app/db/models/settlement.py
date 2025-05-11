# --- START OF FILE app/db/models/settlement.py ---

from sqlalchemy import Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import text
from .base import Base
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

class Settlement(Base):
    """Settlement model for SQLAlchemy ORM"""
    __tablename__ = 'settlements'

    # --- Fields REQUIRED in Python __init__ (Non-Defaults first) ---
    # Foreign Key to worlds table (No Python default, required)
    world_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("worlds.id"),
        nullable=False
        # init=True is default, so keep it in __init__
    )

    # --- Fields OPTIONAL/PROVIDED in Python __init__ (Defaults available) ---
    # Primary Key (Has default, but you provide it)
    entity_id: Mapped[uuid.UUID] = mapped_column(
        "id",  # <<< Explicitly state the DB column name is "id"
        pgUUID(as_uuid=True),
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
        pgUUID(as_uuid=True),
        ForeignKey("characters.id"),
        nullable=True
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
