# --- START OF FILE app/game_state/entities/building_instance.py ---

import uuid
from dataclasses import dataclass, field, KW_ONLY
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import enum

# --- Project Imports ---
from .base import BaseEntity # Assuming this is at app/game_state/entities/base.py

# --- Enums for Building Status ---
class BuildingStatus(enum.Enum):
    """Status of a constructed building instance."""
    UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"
    ACTIVE = "ACTIVE"            # Operational
    INACTIVE = "INACTIVE"          # Not operational (e.g., needs power/workers)
    DAMAGED = "DAMAGED"           # HP below a threshold but not destroyed
    DESTROYED = "DESTROYED"        # HP at or below 0
    UPGRADING = "UPGRADING"         # If upgrades take time
    # PLANNED = "PLANNED"          # Optional: Plot claimed, no resources spent yet

# --- Domain Entity Definition ---
@dataclass
class BuildingInstance(BaseEntity): # Inherit from BaseEntity
    """
    Domain Entity representing a specific constructed building instance in the game world.
    Acts primarily as a data holder. Business logic for state changes (e.g., damage, repair)
    is handled by Managers or Services.
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntity.
    """
    # entity_id: uuid.UUID  (Inherited from BaseEntity)
    # name: str             (Inherited from BaseEntity)

    _: KW_ONLY # Ensures fields below are keyword-only

    # --- Links to Definitions and Location ---
    building_blueprint_id: uuid.UUID
    settlement_id: uuid.UUID

    # --- Instance-Specific State ---
    level: int = 1
    status: BuildingStatus = BuildingStatus.UNDER_CONSTRUCTION
    current_hp: int = 100
    max_hp: int = 100

    inhabitants_count: int = 0
    workers_count: int = 0
    # max_inhabitants_capacity: int = 0 # Consider if this is part of the entity or derived by service
    # max_workers_capacity: int = 0   # Consider if this is part of the entity or derived by service

    construction_progress: float = 0.0
    current_stage_number: int = 1

    stored_resources: Dict[uuid.UUID, int] = field(default_factory=dict)
    assigned_workers_details: Dict[str, int] = field(default_factory=dict)
    active_features: List[uuid.UUID] = field(default_factory=list)
    instance_description: Optional[str] = field(default=None, repr=False)

    # --- Timestamps ---
    # Assuming BaseEntity might provide these. If not, uncomment and adjust __post_init__.
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))

    # --- Initialization Logic ---
    def __post_init__(self):
        """
        Called automatically after the dataclass is initialized.
        Ensures initial state consistency.
        """
        if hasattr(super(), '__post_init__'):
            super().__post_init__() # type: ignore

        # Initial status check - this kind of logic is acceptable in __post_init__
        # as it sets the initial state based on provided data.
        if self.construction_progress < 1.0 and \
           self.status not in (BuildingStatus.DESTROYED, BuildingStatus.UPGRADING) and \
           self.current_stage_number > 0:
             self.status = BuildingStatus.UNDER_CONSTRUCTION
        elif self.construction_progress >= 1.0 and self.status == BuildingStatus.UNDER_CONSTRUCTION:
              self.status = BuildingStatus.ACTIVE

        # Handle updated_at if not set by BaseEntity or constructor
        # This ensures updated_at is at least the creation time initially.
        # Subsequent updates to updated_at would be handled by the service/manager
        # right before saving after a modification.
        if not hasattr(super(), 'updated_at') and self.updated_at is None:
            self.updated_at = self.created_at
        elif hasattr(super(), 'updated_at') and getattr(self, 'updated_at') is None and hasattr(self, 'created_at'):
             setattr(self, 'updated_at', getattr(self, 'created_at'))


    # --- Representation ---
    # Inherits __repr__ from BaseEntity.
    # def __repr__(self) -> str:
    #     base_repr = super().__repr__()
    #     closing_paren_index = base_repr.rfind(')')
    #     if closing_paren_index != -1:
    #         specifics = f", status={self.status.name}, hp={self.current_hp}/{self.max_hp}"
    #         return base_repr[:closing_paren_index] + specifics + base_repr[closing_paren_index:]
    #     return f"{base_repr} (status={self.status.name}, hp={self.current_hp}/{self.max_hp})"

# --- END OF FILE app/game_state/entities/building_instance.py ---