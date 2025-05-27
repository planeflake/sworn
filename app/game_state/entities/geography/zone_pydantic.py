from pydantic import Field, ConfigDict
from uuid import UUID
from typing import Optional, List, Dict, Any

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic
from app.game_state.enums.shared import StatusEnum

class ZonePydantic(BaseEntityPydantic):
    """
    Zone entity representing a geographical area in the game world.
    Inherits 'entity_id' and 'name' from BaseEntityPydantic.
    Zones are areas within a world that can contain settlements, resources, and NPCs.
    """
    # --- Specific Attributes for this Entity ---
    # Optional longer text description
    description: Optional[str] = None
    
    # Foreign keys to other entities
    world_id: Optional[UUID] = None  # Required: The world this zone belongs to
    theme_id: Optional[UUID] = None  # Optional: The primary theme of this zone
    controlling_faction: Optional[UUID] = None  # Optional: The faction controlling this zone
    
    # Collections of related entity IDs
    settlements: List[UUID] = Field(default_factory=list)
    biomes: List[UUID] = Field(default_factory=list)
    
    # Status and other properties
    status: StatusEnum = StatusEnum.ACTIVE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Zone entity to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add zone-specific fields
        zone_data = {
            "id": str(self.entity_id),  # For database/API compatibility
            "description": self.description,
            "world_id": str(self.world_id) if self.world_id else None,
            "theme_id": str(self.theme_id) if self.theme_id else None,
            "controlling_faction": str(self.controlling_faction) if self.controlling_faction else None,
            "settlements": [str(s) for s in self.settlements],
            "biomes": [str(b) for b in self.biomes],
            "status": self.status.value,
        }
        
        data.update(zone_data)
        return data
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "The Dark Forest",
                "description": "A dense, foreboding forest with ancient trees and mysterious creatures",
                "world_id": "550e8400-e29b-41d4-a716-446655440000",
                "theme_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "status": "ACTIVE",
                "biomes": ["550e8400-e29b-41d4-a716-446655440001", "550e8400-e29b-41d4-a716-446655440002"]
            }
        }
    )

# For backward compatibility
ZoneEntity = ZonePydantic