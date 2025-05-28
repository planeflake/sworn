# --- START OF FILE app/game_state/entities/building_upgrade_blueprint_entity.py ---

import uuid
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from ..base import BaseEntity

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
    parent_blueprint_id: Optional[uuid.UUID] = field(default=None)
    effects: Dict[str, Any] = field(default_factory=dict)
    is_initial_choice: bool = False

    # Timestamps are now handled by BaseEntity

# --- END OF FILE app/game_state/entities/building_upgrade_blueprint_entity.py ---