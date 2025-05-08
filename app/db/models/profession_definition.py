# --- START OF FILE app/db/models/profession_definition.py ---

import uuid
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime,
    ForeignKey, UniqueConstraint, Index, func,
    Enum as SQLAlchemyEnum # Import Enum directly for the column type
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID, JSONB, ARRAY # ARRAY needed
from sqlalchemy.sql import text

from .base import Base

# --- Enums ---
class ProfessionCategory(enum.Enum):
    # ... (as before) ...
    CRAFTING = "CRAFTING"
    GATHERING = "GATHERING"
    COMBAT = "COMBAT"
    SOCIAL = "SOCIAL"
    SERVICE = "SERVICE"
    MANAGEMENT = "MANAGEMENT"

class ProfessionUnlockType(enum.Enum):
    # ... (as before) ...
    NPC_TEACHER = "npc_teacher"
    ITEM_MANUAL = "item_manual"
    WORLD_OBJECT = "world_object"
    QUEST_COMPLETION = "quest_completion"
    SKILL_THRESHOLD = "skill_threshold"

# --- Model ---
class ProfessionDefinition(Base):
    __tablename__ = 'profession_definitions'

    id: Mapped[uuid.UUID] = mapped_column(
        pgUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[ProfessionCategory]] = mapped_column(String(50), nullable=True, index=True) # String approach

    skill_requirements: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    available_theme_ids: Mapped[Optional[List[uuid.UUID]]] = mapped_column(ARRAY(pgUUID(as_uuid=True)), nullable=True)

    # --- CHANGE: Storing Unlock Types ---
    # Using PostgreSQL ARRAY of Enums (requires native ENUM type in DB)
    # Option 1a: Native ENUM ARRAY (Cleanest ORM mapping, requires migration management for the ENUM type itself)
    # valid_unlock_methods: Mapped[Optional[List[ProfessionUnlockType]]] = mapped_column(
    #     ARRAY(SQLAlchemyEnum(ProfessionUnlockType, name="profession_unlock_type_enum", create_type=False)),
    #     nullable=True,
    #     comment="List of valid methods (enum values) to unlock this profession."
    # )

    # Option 1b: ARRAY of Strings (Simpler DB setup, validation shifts more to Python)
    valid_unlock_methods: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(50)), # Store enum *values* (strings) in the array
        nullable=True,
        comment="List of valid methods (strings) to unlock this profession. Corresponds to ProfessionUnlockType values."
    )
    # --- END CHANGE ---

    # --- Unlock Conditions Data (Still Needed) ---
    unlock_condition_details: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSONB, nullable=True,
        comment="Detailed data for each unlock type. E.g., [{'type': 'npc_teacher', 'target_id': 'master_smith_prof_id'}, ...]"
        # This still holds the specifics (WHICH NPC, WHICH item)
    )

    # --- Configuration for Logic Handling ---
    python_class_override: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    archetype_handler: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    configuration_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # --- Table Arguments ---
    __table_args__ = (
        Index('ix_profession_definition_category', 'category'),
        # Optional: Add GIN index for ARRAY columns if filtering/searching within them frequently in PG
        # Index('ix_prof_def_valid_unlock_methods', 'valid_unlock_methods', postgresql_using='gin'),
        # Index('ix_prof_def_available_theme_ids', 'available_theme_ids', postgresql_using='gin'),
    )

    def __repr__(self) -> str:
        return f"<ProfessionDefinition(id={self.id!r}, name={self.name!r})>"

# --- END OF FILE app/db/models/profession_definition.py ---