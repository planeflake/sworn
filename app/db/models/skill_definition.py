# --- START OF FILE app/db/models/skill_definition.py ---

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Integer, String, Text, DateTime, func, Index, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship # relationship might be needed if linking back from somewhere
from sqlalchemy.dialects.postgresql import UUID as pgUUID, ARRAY, JSONB # ARRAY for themes

from .base import Base

class SkillDefinition(Base):
    """
    SQLAlchemy ORM Model for Skill Definitions.
    Represents the blueprint or definition of a skill available in the game.
    """
    __tablename__ = 'skill_definitions'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    # Use a unique string identifier as well? Helpful for referencing in configs/code
    # skill_key: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, unique=True, # Ensure name is unique too
        comment="User-facing name of the skill."
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    max_level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=100, server_default='100',
        comment="Maximum level attainable for this skill."
    )

    # Store relevant themes as an array of strings or UUIDs
    themes: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(50)), nullable=True, # Store theme names or IDs
        comment="List of theme names/IDs where this skill is relevant."
    )
    # Or use UUIDs if themes have UUID PKs:
    # themes: Mapped[Optional[List[uuid.UUID]]] = mapped_column(ARRAY(pgUUID(as_uuid=True)), nullable=True)

    # Store base XP curve or related data using _metadata to avoid SQLAlchemy name conflict
    _metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "_metadata", # Use the actual column name in the database
        JSONB, nullable=True,
        comment="Additional data like XP curve type, related stats, etc."
    )

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # --- Table Arguments ---
    __table_args__ = (
        # Index on themes array if using PG and querying often
        # Index('ix_skill_definition_themes', 'themes', postgresql_using='gin'),
        # {'schema': 'my_schema'}
    )

    def __repr__(self) -> str:
        return f"<SkillDefinition(id={self.id!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/skill_definition.py ---