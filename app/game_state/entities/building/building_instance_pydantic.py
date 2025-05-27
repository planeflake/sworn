from pydantic import Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID

# --- Project Imports ---
from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

# Import from the enum module
from app.game_state.enums.building import BuildingStatus

class BuildingInstanceEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing a specific constructed building instance in the game world.
    Acts primarily as a data holder. Business logic for state changes (e.g., damage, repair)
    is handled by Managers or Services.
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntityPydantic.
    """
    # --- Links to Definitions and Location ---
    building_blueprint_id: UUID
    settlement_id: UUID

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

    stored_resources: Dict[UUID, int] = Field(default_factory=dict)
    assigned_workers_details: Dict[str, int] = Field(default_factory=dict)
    active_features: List[UUID] = Field(default_factory=list)
    instance_description: Optional[str] = None

    # Status validation logic that was in __post_init__
    @field_validator('status')
    @classmethod
    def validate_status(cls, v, values):
        """Validate and adjust status based on construction progress"""
        # We can only perform this validation if we have all the needed values
        if 'construction_progress' in values.data and 'current_stage_number' in values.data:
            construction_progress = values.data['construction_progress']
            current_stage_number = values.data['current_stage_number']
            
            if construction_progress < 1.0 and \
               v not in (BuildingStatus.DESTROYED, BuildingStatus.UPGRADING) and \
               current_stage_number > 0:
                return BuildingStatus.UNDER_CONSTRUCTION
            elif construction_progress >= 1.0 and v == BuildingStatus.UNDER_CONSTRUCTION:
                return BuildingStatus.ACTIVE
        
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert BuildingInstanceEntity to a dictionary with safe serialization."""
        # Get base entity fields
        result = super().to_dict()
        
        # Add building instance specific fields
        building_data = {
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
        
        result.update(building_data)
        if self.instance_description:
            result["instance_description"] = self.instance_description
        return result
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Town Hall",
                "building_blueprint_id": "550e8400-e29b-41d4-a716-446655440000",
                "settlement_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "level": 1,
                "status": "ACTIVE",
                "current_hp": 100,
                "max_hp": 100,
                "construction_progress": 1.0,
                "current_stage_number": 1
            }
        }
    )

# For backward compatibility
BuildingInstance = BuildingInstanceEntityPydantic