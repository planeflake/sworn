# --- START OF FILE app/game_state/entities/building_instance.py ---

import uuid
from dataclasses import dataclass, field, KW_ONLY
from typing import Optional, List, Dict, Any

# --- Project Imports ---
from .base import BaseEntity # Assuming this is at app/game_state/entities/base.py

# Import from the enum module
from app.game_state.enums.building import BuildingStatus

# --- Domain Entity Definition ---
@dataclass(kw_only=True)
class BuildingInstanceEntity(BaseEntity): # Inherit from BaseEntity
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
    # created_at and updated_at now come from BaseEntity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert BuildingInstanceEntity to a dictionary with safe serialization."""
        result = {
            "id": str(self.entity_id),
            "name": self.name,
            "building_blueprint_id": str(self.building_blueprint_id),
            "settlement_id": str(self.settlement_id),
            "level": self.level,
            "status": self.status.value,
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "inhabitants_count": self.inhabitants_count,
            "workers_count": self.workers_count,
            "construction_progress": self.construction_progress,
            "current_stage_number": self.current_stage_number,
            "stored_resources": {str(k): v for k, v in self.stored_resources.items()},
            "assigned_workers_details": self.assigned_workers_details,
            "active_features": [str(f) for f in self.active_features],
        }
        
        # Include the base entity fields (including timestamps)
        base_data = super().to_dict()
        result.update(base_data)
        if self.instance_description:
            result["instance_description"] = self.instance_description
        return result

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

        # BaseEntity now handles timestamp setup


    # --- Representation ---
    # Inherits __repr__ from BaseEntity.
    # def __repr__(self) -> str:
    #     base_repr = super().__repr__()
    #     closing_paren_index = base_repr.rfind(')')
    #     if closing_paren_index != -1:
    #         specifics = f", status={self.status.name}, hp={self.current_hp}/{self.max_hp}"
    #         return base_repr[:closing_paren_index] + specifics + base_repr[closing_paren_index:]
    #     return f"{base_repr} (status={self.status.name}, hp={self.current_hp}/{self.max_hp})"

# For backward compatibility
BuildingInstance = BuildingInstanceEntity

# --- END OF FILE app/game_state/entities/building_instance.py ---