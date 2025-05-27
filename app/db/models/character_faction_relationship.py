# --- FILE: app/db/models/character_faction_relationship.py ---

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum

from sqlalchemy import ForeignKey, Integer, DateTime, func, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql as pg

from .base import Base

if TYPE_CHECKING:
    from .character import Character
    from .faction import Faction

class RelationshipStatusEnum(Enum):
    """Relationship status between character and faction."""
    ALLY = "ally"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"
    ENEMY = "enemy"
    UNKNOWN = "unknown"

class CharacterFactionRelationship(Base):
    """
    SQLAlchemy ORM Model for Character-Faction relationships.
    Tracks individual character relationships with different factions.
    """
    __tablename__ = "character_faction_relationships"
    __table_args__ = {'extend_existing': True}

    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    character_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("characters.id", name="fk_char_faction_rel_character", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    faction_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("factions.id", name="fk_char_faction_rel_faction", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationship metrics
    reputation_score: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="Reputation score from -100 (enemy) to +100 (ally)"
    )
    
    relationship_status: Mapped[RelationshipStatusEnum] = mapped_column(
        SQLAlchemyEnum(RelationshipStatusEnum, name="relationship_status_enum", create_type=False),
        nullable=False, default=RelationshipStatusEnum.NEUTRAL
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_interaction: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    character: Mapped["Character"] = relationship(
        "Character",
        back_populates="faction_relationships",
        lazy="selectin"
    )
    
    faction: Mapped["Faction"] = relationship(
        "Faction",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<CharacterFactionRelationship(character_id={self.character_id!r}, faction_id={self.faction_id!r}, status={self.relationship_status.value})>"