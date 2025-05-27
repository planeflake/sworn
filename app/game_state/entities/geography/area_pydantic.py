from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import Field, ConfigDict

from app.game_state.enums.shared import StatusEnum
from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class AreaEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing an area in a zone within the game world.
    Inherits common fields from BaseEntityPydantic.
    """
    description: Optional[str] = None
    zone_id: UUID
    world_id: UUID
    biome_id: Optional[UUID] = None
    theme_id: Optional[UUID] = None
    controlling_faction: Optional[UUID] = None
    
    # Geographical properties
    size: float = 1.0
    coordinates: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0})
    elevation: float = 0.0
    
    # Collections of related entity IDs
    settlement_ids: List[UUID] = Field(default_factory=list)
    resource_node_ids: List[UUID] = Field(default_factory=list)
    character_ids: List[UUID] = Field(default_factory=list)
    
    # Status and other properties
    status: StatusEnum = StatusEnum.ACTIVE
    is_discovered: bool = False
    danger_level: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add area-specific fields
        area_data = {
            "id": str(self.entity_id),  # For compatibility with API
            "description": self.description,
            "zone_id": str(self.zone_id) if self.zone_id else None,
            "world_id": str(self.world_id) if self.world_id else None,
            "biome_id": str(self.biome_id) if self.biome_id else None,
            "theme_id": str(self.theme_id) if self.theme_id else None,
            "controlling_faction": str(self.controlling_faction) if self.controlling_faction else None,
            "size": self.size,
            "coordinates": self.coordinates,
            "elevation": self.elevation,
            "settlement_ids": [str(s) for s in self.settlement_ids],
            "resource_node_ids": [str(r) for r in self.resource_node_ids],
            "character_ids": [str(c) for c in self.character_ids],
            "status": self.status.value,
            "is_discovered": self.is_discovered,
            "danger_level": self.danger_level,
        }
        
        data.update(area_data)
        return data
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Dark Forest",
                "description": "A dense forest with limited visibility",
                "zone_id": "550e8400-e29b-41d4-a716-446655440000",
                "world_id": "550e8400-e29b-41d4-a716-446655440001",
                "biome_id": "550e8400-e29b-41d4-a716-446655440002",
                "theme_id": "550e8400-e29b-41d4-a716-446655440003",
                "size": 2.5,
                "coordinates": {"x": 150, "y": 75},
                "elevation": 250.5,
                "status": "ACTIVE",
                "is_discovered": True,
                "danger_level": 3
            }
        }
    )

# For backward compatibility
Area = AreaEntityPydantic