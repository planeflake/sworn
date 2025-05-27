# --- FILE: app/db/models/character.py ---

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Integer, String, DateTime, func, ForeignKey, Boolean,
    Enum as SQLAlchemyEnum, Text, Table, Column, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects import postgresql as pg

from .base import Base
from app.game_state.enums.character import CharacterTypeEnum, CharacterStatusEnum, CharacterTraitEnum

# TYPE CHECKING IMPORTS
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .item import Item
    from .location_instance import LocationInstance
    from .skill import Skill
    from .building_instance import BuildingInstanceDB
    from .faction import Faction
    from .character_faction_relationship import CharacterFactionRelationship

# Association Table for Character <-> Skill
character_skills_association = Table(
    "character_skills",
    Base.metadata,
    Column("character_id", pg.UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", pg.UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    Column("level", Integer, nullable=False, default=1, server_default='1'),
    Column("xp", Integer, nullable=False, default=0, server_default='0')
)

class Character(Base):
    __tablename__ = 'characters'

    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    character_type: Mapped[CharacterTypeEnum] = mapped_column(
        SQLAlchemyEnum(CharacterTypeEnum, name="character_type_enum", create_type=False),
        nullable=False, index=True
    )
    character_traits: Mapped[List[CharacterTraitEnum]] = mapped_column(
        pg.ARRAY(SQLAlchemyEnum(CharacterTraitEnum, name="character_trait_enum", create_type=False)),
        nullable=True, default=list, server_default="{}"
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default='1')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default='true')
    status: Mapped[CharacterStatusEnum] = mapped_column(
        SQLAlchemyEnum(CharacterStatusEnum, name="character_status_enum", create_type=False),
        nullable=False, default=CharacterStatusEnum.ALIVE
    )
    stats: Mapped[Optional[Dict[str, Any]]] = mapped_column(pg.JSONB, nullable=True, default=dict)
    equipment: Mapped[Optional[Dict[str, Any]]] = mapped_column(pg.JSONB, nullable=True, default=dict)

    world_id: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("worlds.id", name="fk_character_world_id"),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    current_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("location_entities.id", name="fk_char_location_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    current_building_home_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("building_instances.id", name="fk_char_home_building_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    current_building_workplace_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("building_instances.id", name="fk_char_work_building_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Default faction this character belongs to
    default_faction_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        pg.UUID(as_uuid=True),
        ForeignKey("factions.id", name="fk_character_default_faction", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Relationships
    items: Mapped[List["Item"]] = relationship("Item", back_populates="owner", lazy="selectin", cascade="all, delete-orphan")

    current_location: Mapped[Optional["LocationInstance"]] = relationship(
        "LocationInstance",  # Updated to use the new model name
        foreign_keys=[current_location_id],
        back_populates="characters_at_location",
        lazy="selectin"
    )

    skills: Mapped[List["Skill"]] = relationship(
        "Skill",
        secondary=character_skills_association,
        back_populates="characters_with_skill",
        lazy="selectin"
    )

    home_building: Mapped[Optional["BuildingInstanceDB"]] = relationship(
        "BuildingInstanceDB",
        foreign_keys=[current_building_home_id],
        back_populates="residents",
        lazy="selectin"
    )

    work_building: Mapped[Optional["BuildingInstanceDB"]] = relationship(
        "BuildingInstanceDB",
        foreign_keys=[current_building_workplace_id],
        back_populates="workers",
        lazy="selectin"
    )
    
    # Default faction relationship
    default_faction: Mapped[Optional["Faction"]] = relationship(
        "Faction",
        foreign_keys=[default_faction_id],
        lazy="selectin"
    )
    
    # Specific faction relationships
    faction_relationships: Mapped[List["CharacterFactionRelationship"]] = relationship(
        "CharacterFactionRelationship",
        back_populates="character",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Character(id={self.id!r}, name={self.name!r}, type={self.character_type.name})>"
