from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field, ConfigDict

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class ResourceBlueprintEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing a Resource Blueprint.
    Inherits common fields from BaseEntityPydantic.
    """
    description: Optional[str] = None
    theme_id: Optional[UUID] = None
    rarity: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add resource-specific fields
        resource_data = {
            "id": str(self.entity_id),  # For compatibility with API
            "description": self.description,
            "theme_id": str(self.theme_id) if self.theme_id else None,
            "rarity": self.rarity,
        }
        
        data.update(resource_data)
        return data
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Iron Ore",
                "description": "Raw iron ore extracted from mines",
                "theme_id": "550e8400-e29b-41d4-a716-446655440000",
                "rarity": "common",
                "tags": ["metal", "ore", "mining"]
            }
        }
    )

# For backward compatibility 
ResourceBlueprint = ResourceBlueprintEntityPydantic