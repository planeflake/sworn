# --- START OF FILE app/game_state/entities/building_upgrade_blueprint_entity.py ---

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from .base import BaseEntity

@dataclass(kw_only=True)
class BuildingUpgradeBlueprintEntity(BaseEntity):
    """
    Domain Entity for a Building Upgrade Blueprint.
    'name' is the unique internal key (e.g., 'arrow_slits_stone_tower').
    """
    # entity_id: uuid.UUID (from BaseEntity)
    # name: str (unique internal key from BaseEntity)

    display_name: str  = None # User-facing name
    description: Optional[str] = None

    target_blueprint_criteria: Dict[str, Any] = field(default_factory=dict)
    prerequisites: Dict[str, Any] = field(default_factory=dict)

    resource_cost: Dict[uuid.UUID, int] = field(default_factory=dict) # resource_id (UUID) -> count
    profession_cost: Dict[uuid.UUID, int] = field(default_factory=dict) # profession_definition_id (UUID) -> count
    duration_days: int = 1

    effects: Dict[str, Any] = field(default_factory=dict)
    is_initial_choice: bool = False

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = self.created_at

# --- END OF FILE app/game_state/entities/building_upgrade_blueprint_entity.py ---