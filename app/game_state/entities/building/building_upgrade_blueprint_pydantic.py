from pydantic import Field, ConfigDict
from uuid import UUID
from typing import Optional, Dict, Any

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class BuildingUpgradeBlueprintEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity for a Building Upgrade Blueprint.
    'name' is the unique internal key (e.g., 'arrow_slits_stone_tower').
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntityPydantic.
    """
    display_name: Optional[str] = None  # User-facing name
    description: Optional[str] = None

    target_blueprint_criteria: Dict[str, Any] = Field(default_factory=dict)
    prerequisites: Dict[str, Any] = Field(default_factory=dict)

    resource_cost: Dict[UUID, int] = Field(default_factory=dict)  # resource_id (UUID) -> count
    profession_cost: Dict[UUID, int] = Field(default_factory=dict)  # profession_definition_id (UUID) -> count
    duration_days: int = 1
    parent_blueprint_id: Optional[UUID] = Field(default_factory=UUID)
    effects: Dict[str, Any] = Field(default_factory=dict)
    is_initial_choice: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add upgrade-specific fields
        upgrade_data = {
            "display_name": self.display_name,
            "description": self.description,
            "target_blueprint_criteria": self.target_blueprint_criteria,
            "prerequisites": self.prerequisites,
            "resource_cost": {str(k): v for k, v in self.resource_cost.items()},
            "profession_cost": {str(k): v for k, v in self.profession_cost.items()},
            "duration_days": self.duration_days,
            "effects": self.effects,
            "is_initial_choice": self.is_initial_choice,
        }
        
        data.update(upgrade_data)
        return data
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "arrow_slits_stone_tower",
                "display_name": "Arrow Slits",
                "description": "Narrow openings in the tower walls for archers",
                "target_blueprint_criteria": {
                    "type": "tower",
                    "attributes": ["stone"]
                },
                "resource_cost": {
                    "550e8400-e29b-41d4-a716-446655440000": 50
                },
                "profession_cost": {
                    "550e8400-e29b-41d4-a716-446655440001": 1
                },
                "duration_days": 3,
                "effects": {
                    "defense": 10,
                    "ranged_damage": 5
                },
                "is_initial_choice": False
            }
        }
    )

# For backward compatibility
BuildingUpgradeBlueprintEntity = BuildingUpgradeBlueprintEntityPydantic