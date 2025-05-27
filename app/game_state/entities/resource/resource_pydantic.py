from pydantic import Field, ConfigDict
from app.game_state.enums.shared import RarityEnum, StatusEnum
from app.game_state.entities.core.base_pydantic import BaseEntityPydantic
from uuid import UUID
from typing import Optional, Dict, Any

class ResourceEntityPydantic(BaseEntityPydantic):
    """
    Represents a Resource TYPE in the game (Domain Entity).
    Uses resource_id as its primary identifier.
    """
    # --- Primary Identifier ---
    resource_id: UUID
    
    # --- Fields with defaults (Specific to ResourceEntity) ---
    rarity: RarityEnum = RarityEnum.COMMON
    status: StatusEnum = StatusEnum.ACTIVE
    theme_id: Optional[UUID] = None
    stack_size: int = 100
    
    # --- Optional fields (Specific to ResourceEntity) ---
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ResourceEntity to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add resource-specific fields
        resource_data = {
            "id": str(self.entity_id),
            "name": self.name,
            "resource_id": str(self.resource_id),
            "rarity": self.rarity.value,
            "status": self.status.value,
            "theme_id": str(self.theme_id) if self.theme_id else None,
            "stack_size": self.stack_size,
            "description": self.description,
        }
        
        data.update(resource_data)
        return data
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Iron Ore",
                "resource_id": "550e8400-e29b-41d4-a716-446655440000",
                "rarity": "COMMON",
                "status": "ACTIVE",
                "theme_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "stack_size": 100,
                "description": "Raw iron ore that can be smelted into iron ingots"
            }
        }
    )

# For backward compatibility
Resource = ResourceEntityPydantic