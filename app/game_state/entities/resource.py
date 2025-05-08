# --- START OF FILE app/game_state/entities/resource.py ---

from dataclasses import dataclass, field, KW_ONLY
from app.game_state.enums.shared import RarityEnum, StatusEnum
# Import the actual BaseEntity
from .base import BaseEntity
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime

@dataclass
class ResourceEntity(BaseEntity): # Inherits from BaseEntity
    """
    Represents a Resource TYPE in the game (Domain Entity).
    Uses resource_id as its primary identifier.
    Correctly orders fields respecting defaults from BaseEntity.
    """
    # --- Primary Identifier (Required, Positional or Keyword) ---
    # Non-default, comes first
    resource_id: UUID

    # --- Keyword-Only Separator ---
    _: KW_ONLY

    # --- Keyword-Only, REQUIRED field ---
    # Non-default, comes after KW_ONLY
    # name: str # REMOVE this - we will re-declare the one from BaseEntity below

    # --- Keyword-Only, Fields with defaults (Specific to ResourceEntity) ---
    rarity: RarityEnum = RarityEnum.COMMON
    status: StatusEnum = StatusEnum.ACTIVE
    theme_id: Optional[UUID] = None
    stack_size: int = 100

    # --- Keyword-Only, Optional fields (Specific to ResourceEntity) ---
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # --- Keyword-Only, Re-declared fields from BaseEntity (with defaults) ---
    # Place inherited fields with defaults *last* to ensure correct __init__ order.
    # Use the same default as defined in BaseEntity.
    entity_id: UUID = field(default_factory=uuid4) # Re-declared from BaseEntity
    name: str = "Unnamed Entity"                   # Re-declared from BaseEntity


# --- END OF FILE app/game_state/entities/resource.py ---