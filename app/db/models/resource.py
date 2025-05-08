# --- START - app/db/models/resource.py ---

import uuid
import enum
from datetime import datetime
from typing import Optional

# Core SQLAlchemy imports
from sqlalchemy import (
    Integer, String, DateTime, func, Enum, Text # Make sure Text is imported
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.sql import text # Needed for server_default UUID
from sqlalchemy import ForeignKey
from .base import Base
from app.game_state.enums.shared import RarityEnum, StatusEnum

class Resource(Base):
    """
    SQLAlchemy ORM Model for Resource Types.
    """
    __tablename__ = 'resources'

    resource_id: Mapped[uuid.UUID] = mapped_column(
        "id",
        pgUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(
        String(100), # Correct: Type provided
        nullable=False,
        unique=True,
        index=True
    )

    # --- CORRECTED description ---
    description: Mapped[Optional[str]] = mapped_column(
        Text, # <<< Provide the column type (Text for long strings)
        nullable=True
    )
    # -----------------------------

    rarity: Mapped[Optional[RarityEnum]] = mapped_column(
        Enum(RarityEnum, name="rarity_enum", create_type=False), # Correct: Type provided
        nullable=True,
        default=RarityEnum.COMMON,
        index=True
    )

    stack_size: Mapped[int] = mapped_column(
        Integer, # Correct: Type provided
        nullable=False,
        default=100,
        server_default='100'
    )

    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, name="status_enum", create_type=False), # Correct: Type provided
        nullable=False,
        default=StatusEnum.ACTIVE,
        server_default=StatusEnum.ACTIVE.value,
        index=True
    )

    theme_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("themes.id"),  # Assuming it references a themes table
        nullable=False  # This matches your database constraint
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), # Correct: Type provided
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), # Correct: Type provided
        onupdate=func.now(),
        server_default=func.now(),
        nullable=True
    )

# --- END - app/db/models/resource.py ---