# --- START OF FILE app/db/models/character.py ---

import uuid
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Integer, String, DateTime, func, ForeignKey, Boolean, Enum as SQLAlchemyEnum, Text, Table, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB
from sqlalchemy.sql import text

from .base import Base
from app.game_state.enums.character import CharacterTypeEnum, CharacterStatusEnum # Assuming this path is correct

# TYPE CHECKING IMPORTS for RELATIONSHIPS
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .item import Item
    from .location import Location
    from .skill import Skill
    # from .player_account import PlayerAccount # If you create this model
    from .building_instance import BuildingInstanceDB # <<< ADD THIS IMPORT

# --- Association Table for Character <-> Skill (Many-to-Many) ---
# This needs to be defined where both Character and Skill can see it,
# or imported if in its own file.
character_skills_association = Table(
    "character_skills",
    Base.metadata,
    Column("character_id", pgUUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", pgUUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True), # Assumes skills.id is UUID
    Column("level", Integer, nullable=False, default=1, server_default='1'),
    Column("xp", Integer, nullable=False, default=0, server_default='0')
)

class Character(Base):
    """
    SQLAlchemy ORM Model for Characters (Players and NPCs).
    """
    __tablename__ = 'characters'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    character_type: Mapped[CharacterTypeEnum] = mapped_column(
        SQLAlchemyEnum(CharacterTypeEnum, name="character_type_enum", create_type=False),
        nullable=False, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default='1')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default='true')
    status: Mapped[CharacterStatusEnum] = mapped_column(
        SQLAlchemyEnum(CharacterStatusEnum, name="character_status_enum", create_type=False),
        nullable=False, default=CharacterStatusEnum.ALIVE
    )
    stats: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True, default=lambda: {})
    equipment: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True, default=lambda: {})

    world_id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("worlds.id", name="fk_character_world_id"),
        nullable=False, # Assuming a character must belong to a world
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=True
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Foreign Keys ---
    #player_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    #    pgUUID(as_uuid=True),
    #    ForeignKey("player_accounts.id", name="fk_char_player_account_id", use_alter=True, ondelete="SET NULL"), # Assuming player_accounts table
    #    nullable=True, unique=True, index=True
    #)
    current_location_id: Mapped[Optional[uuid.UUID]] = mapped_column(
       pgUUID(as_uuid=True),
       ForeignKey("locations.id", name="fk_char_location_id", ondelete="SET NULL"), # Assuming locations table
       nullable=True,
       index=True
    )

    # --- BUILDING ASSIGNMENT FOREIGN KEYS ---
    current_building_home_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("building_instances.id", name="fk_char_home_building_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    current_building_workplace_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        pgUUID(as_uuid=True),
        ForeignKey("building_instances.id", name="fk_char_work_building_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    # --- END BUILDING ASSIGNMENT FOREIGN KEYS ---


    # --- Relationships ---
    items: Mapped[List["Item"]] = relationship(
        "Item",
        back_populates="owner",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


    current_location: Mapped[Optional["Location"]] = relationship(
       "Location",
       foreign_keys=[current_location_id],
       back_populates="characters_at_location", # Ensure Location model has 'characters_at_location'
       lazy="selectin"
    )

    skills: Mapped[List["Skill"]] = relationship(
        "Skill",
        secondary=character_skills_association,
        back_populates="characters_with_skill", # Updated back_populates name for clarity
        lazy="selectin"
    )

    # Optional: Relationship to PlayerAccount (if PlayerAccount model exists)
    # player_account: Mapped[Optional["PlayerAccount"]] = relationship(
    #     "PlayerAccount",
    #     foreign_keys=[player_account_id],
    #     back_populates="character" # Assumes PlayerAccount has 'character' relationship
    # )

    # --- BUILDING ASSIGNMENT RELATIONSHIPS ---
    home_building: Mapped[Optional["BuildingInstanceDB"]] = relationship(
        "BuildingInstanceDB",
        foreign_keys=[current_building_home_id],
        back_populates="residents", # This name needs to exist in BuildingInstanceDB
        lazy="selectin"
    )
    work_building: Mapped[Optional["BuildingInstanceDB"]] = relationship(
        "BuildingInstanceDB",
        foreign_keys=[current_building_workplace_id],
        back_populates="workers", # This name needs to exist in BuildingInstanceDB
        lazy="selectin"
    )
    # --- END BUILDING ASSIGNMENT RELATIONSHIPS ---

    def __repr__(self) -> str:
        return f"<Character(id={self.id!r}, name={self.name!r}, type={self.character_type.name})>"

# --- END OF FILE app/db/models/character.py ---