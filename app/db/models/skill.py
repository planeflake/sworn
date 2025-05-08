# --- START OF FILE app/db/models/skill.py ---

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Integer, String, Text, DateTime, func, Table, Column, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.sql import text
from .base import Base
# Import Character only needed for type hinting if using TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .character import Character

# --- Association Table Definition (Many-to-Many Character <-> Skill) ---
# Place this *before* the Skill class if Skill references it, or import if separate file
character_skills_association = Table(
    "character_skills", # Table name in the database
    Base.metadata,
    Column("character_id", pgUUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", pgUUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    # Add other columns to the association if needed (e.g., proficiency level/xp)
    Column("level", Integer, nullable=False, default=1, server_default='1'),
    Column("xp", Integer, nullable=False, default=0, server_default='0')
)
# --- END Association Table ---


class Skill(Base):
    """
    SQLAlchemy ORM Model for Skill Definitions.
    Represents the definition of a skill available in the game.
    """
    __tablename__ = 'skills' # Table for skill *definitions*

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    # Use 'skill_id_name' or similar if you prefer a unique string identifier
    # skill_id_name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationship to Characters who have learned this skill (via association table)
    characters: Mapped[List["Character"]] = relationship(
        "Character",
        secondary=character_skills_association, # Link through the association table
        back_populates="skills", # Matches 'skills' relationship in Character model
        lazy="selectin"
    )

    # Optional: Link to themes if skills are theme-specific
    # theme_id: Mapped[Optional[uuid.UUID]] = mapped_column(pgUUID(as_uuid=True), ForeignKey("themes.id"), nullable=True, index=True)

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Skill(id={self.id!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/skill.py ---