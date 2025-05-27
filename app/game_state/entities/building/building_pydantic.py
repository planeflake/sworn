from pydantic import Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class BuildingEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing a building concept in the game world.
    This is different from BuildingInstanceEntity, which represents a specific constructed instance.
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntityPydantic.
    """
    description: Optional[str] = None
    
    # --- Building Metadata ---
    type: str = "generic"
    category: str = "generic"
    tier: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert BuildingEntity to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add building-specific fields
        building_data = {
            "id": str(self.entity_id),
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "category": self.category,
            "tier": self.tier,
        }
        
        data.update(building_data)
        return data
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Town Hall",
                "description": "A central administrative building",
                "type": "administrative",
                "category": "civic",
                "tier": 1
            }
        }
    )

# For backward compatibility
Building = BuildingEntityPydantic