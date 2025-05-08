# --- START OF FILE app/game_state/entities/building_instance.py ---

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import enum

# --- Project Imports ---
from .base import BaseEntity # Import the BaseEntity

# --- Enums for Building Status ---
class BuildingStatus(enum.Enum):
    """Status of a constructed building instance."""
    UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"
    ACTIVE = "ACTIVE"            # Operational
    INACTIVE = "INACTIVE"          # Not operational (e.g., needs power/workers)
    DAMAGED = "DAMAGED"           # HP below a threshold but not destroyed
    DESTROYED = "DESTROYED"        # HP at or below 0
    UPGRADING = "UPGRADING"         # If upgrades take time

# --- Domain Entity Definition ---
@dataclass
class BuildingInstance(BaseEntity): # Inherit from BaseEntity
    """
    Domain Entity representing a specific constructed building instance in the game world.
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntity.
    """

    # --- Links to Definitions and Location ---
    # Use entity_id from BaseEntity as the primary identifier for this instance

    building_blueprint_id: uuid.UUID # Link to the BuildingBlueprint definition
    settlement_id: uuid.UUID         # Link to the Settlement where it's located
    # world_id: uuid.UUID            # Optional: Direct link to world if needed, often derivable via settlement

    # --- Instance-Specific State ---
    level: int = 1                      # Current level of this specific building instance
    status: BuildingStatus = BuildingStatus.ACTIVE # Current operational status
    current_hp: int = 100               # Current health points
    max_hp: int = 100                   # Maximum health points (likely set based on blueprint + level)

    # Inhabitants (if applicable to this building type)
    inhabitants: int = 0                # Current number of inhabitants/workers
    max_inhabitants: int = 0            # Capacity (likely set based on blueprint + level)

    # Construction/Upgrade State
    construction_progress: float = 1.0  # 0.0 to 1.0, where 1.0 means fully constructed/upgraded
    current_upgrade_stage: Optional[int] = None # If upgrades have stages linked back to blueprint stages

    # Storage (if applicable) - Resource ID -> Quantity
    stored_resources: Dict[uuid.UUID, int] = field(default_factory=dict)

    # Assigned Workers (if applicable) - Profession Name/ID -> Count
    assigned_workers: Dict[str, int] = field(default_factory=dict)

    # Optional description for THIS instance (e.g., "The slightly burnt Inn")
    instance_description: Optional[str] = field(default=None, repr=False) # Example: Exclude from default repr

    # --- Timestamps ---
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None # Should be updated on state changes

    # --- Initialization Logic ---
    def __post_init__(self):
        """
        Called automatically after the dataclass is initialized.
        Handles setting initial status and updated_at.
        """
        # Set initial status based on construction progress
        if self.construction_progress < 1.0 and self.status not in (BuildingStatus.DESTROYED, BuildingStatus.UPGRADING):
             self.status = BuildingStatus.UNDER_CONSTRUCTION
        elif self.construction_progress >= 1.0 and self.status == BuildingStatus.UNDER_CONSTRUCTION:
              self.status = BuildingStatus.ACTIVE # Ensure active if loaded as constructed

        # Set initial updated_at timestamp
        if self.updated_at is None:
            self.updated_at = self.created_at

        # We could potentially fetch max_hp/max_inhabitants based on level/blueprint here,
        # BUT that usually requires accessing blueprint data, which is better handled
        # in a Service/Manager during creation/loading, not in the entity's __post_init__.

    # --- Representation ---
    # Inherits __repr__ from BaseEntity (shows entity_id, name).
    # Uncomment and customize below if you want more detail.
    # def __repr__(self) -> str:
    #     base_repr = super().__repr__()
    #     closing_paren_index = base_repr.rfind(')')
    #     specifics = f", level={self.level}, status={self.status.name}, hp={self.current_hp}/{self.max_hp}"
    #     return base_repr[:closing_paren_index] + specifics + base_repr[closing_paren_index:]


# --- END OF FILE app/game_state/entities/building_instance.py ---