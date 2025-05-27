# --- START OF FILE app/game_state/entities/resource_blueprint.py ---

from dataclasses import dataclass, field, KW_ONLY
from app.game_state.enums.shared import RarityEnum, StatusEnum
from ..base import BaseEntity
from uuid import UUID, uuid4
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass(kw_only=True)
class ResourceEntity(BaseEntity):
    """
    Represents a Resource TYPE in the game (Domain Entity).
    Uses resource_id as its primary identifier.
    Correctly orders fields respecting defaults from BaseEntity.
    """
    # --- Primary Identifier (Required, Positional or Keyword) ---
    resource_id: UUID

    # --- Keyword-Only Separator ---
    _: KW_ONLY

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
    entity_id: UUID = field(default_factory=uuid4)
    name: str = "Unnamed Entity"

    def __post_init__(self):
        # Ensure entity_id is set
        if self.entity_id is None:
            self.entity_id = uuid4()
            
        # Set created_at if not provided
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert ResourceEntity to a dictionary with safe serialization."""
        # Manually create dictionary instead of using asdict to avoid inheritance issues
        data = {
            "id": str(self.entity_id),
            "name": self.name,
            "resource_id": str(self.resource_id),
            "rarity": self.rarity.value,
            "status": self.status.value,
            "theme_id": str(self.theme_id) if self.theme_id else None,
            "stack_size": self.stack_size,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        return data

# --- END OF FILE app/game_state/entities/resource_blueprint.py ---