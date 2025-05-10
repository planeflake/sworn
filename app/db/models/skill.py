# --- START OF FILE app/db/models/skill.py ---

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Integer, String, Text, DateTime, func, Table, Column, ForeignKey, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from .base import Base

# TYPE CHECKING IMPORTS
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .character import Character # This import should now work if character_skills_association is defined first

# --- Association Table Definition (Many-to-Many Character <-> Skill) ---
# It's often good practice to define association tables before the models that use them,
# or ensure they are imported if defined elsewhere (like in character.py).
# If character_skills_association is defined in character.py, you might need to
# import it here, or ensure character.py is imported before skill.py in __init__.py
# For simplicity, let's assume it's defined here if not already in character.py
# and character.py will use the string "character_skills_association"

# Re-defining it here for completeness in this file,
# BUT ensure it's defined ONLY ONCE in your project.
# If defined in character.py, remove or comment out this definition.
# character_skills_association = Table(
#     "character_skills",
#     Base.metadata,
#     Column("character_id", pgUUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
#     Column("skill_id", pgUUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
#     Column("level", Integer, nullable=False, default=1, server_default='1'),
#     Column("xp", Integer, nullable=False, default=0, server_default='0')
# )
# Instead, import it if it's defined in character.py:
from .character import character_skills_association

class Skill(Base):
    """
    SQLAlchemy ORM Model for Skill Definitions.
    """
    __tablename__ = 'skills'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=100, server_default='100')

    # Relationship to Characters who have learned this skill
    characters_with_skill: Mapped[List["Character"]] = relationship( # Renamed for clarity
        "Character",
        secondary=character_skills_association,
        back_populates="skills", # Matches 'skills' relationship in Character model
        lazy="selectin"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=True)

    def __repr__(self) -> str:
        return f"<Skill(id={self.id!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/skill.py ---