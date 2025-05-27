from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import Field, BaseModel, ConfigDict

from app.game_state.enums.shared import StatusEnum
from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class ResourceNodeResourceEntityPydantic(BaseModel):
    """
    Entity representing a resource within a resource node.
    """
    resource_id: UUID
    is_primary: bool = True
    chance: float = 1.0
    amount_min: int = 1
    amount_max: int = 1
    purity: float = 1.0
    rarity: Optional[str] = "common"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary with safe serialization."""
        data = self.model_dump()
        # For backward compatibility
        data["_metadata"] = data.pop("metadata", {})
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceNodeResourceEntityPydantic":
        """Create an instance from a dictionary."""
        # Handle old _metadata key
        if "_metadata" in data and "metadata" not in data:
            data["metadata"] = data.pop("_metadata")
        return cls(**data)
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


class ResourceNodeEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing a resource node in the game world.
    Inherits common fields from BaseEntityPydantic.
    """
    description: Optional[str] = None
    blueprint_id: Optional[UUID] = None
    theme_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    area_id: Optional[UUID] = None
    depleted: bool = False
    status: StatusEnum = StatusEnum.PENDING
    resource_links: List[ResourceNodeResourceEntityPydantic] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add resource node-specific fields
        node_data = {
            "id": str(self.entity_id),  # For compatibility with API
            "description": self.description,
            "blueprint_id": str(self.blueprint_id) if self.blueprint_id else None,
            "theme_id": str(self.theme_id) if self.theme_id else None,
            "zone_id": str(self.zone_id) if self.zone_id else None,
            "area_id": str(self.area_id) if self.area_id else None,
            "depleted": self.depleted,
            "status": self.status.value,
            "resource_links": [link.to_dict() for link in self.resource_links],
        }
        
        data.update(node_data)
        return data
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Iron Vein",
                "description": "A rich vein of iron ore",
                "blueprint_id": "550e8400-e29b-41d4-a716-446655440000",
                "theme_id": "550e8400-e29b-41d4-a716-446655440001",
                "zone_id": "550e8400-e29b-41d4-a716-446655440002",
                "depleted": False,
                "status": "ACTIVE",
                "resource_links": [
                    {
                        "resource_id": "550e8400-e29b-41d4-a716-446655440003",
                        "is_primary": True,
                        "chance": 1.0,
                        "amount_min": 5,
                        "amount_max": 10,
                        "purity": 0.8,
                        "rarity": "common"
                    }
                ]
            }
        }
    )

# For backward compatibility
ResourceNodeResource = ResourceNodeResourceEntityPydantic
ResourceNode = ResourceNodeEntityPydantic