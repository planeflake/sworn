from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import Field, BaseModel, ConfigDict

from app.game_state.enums.shared import StatusEnum
from app.game_state.entities.core.base_pydantic import BaseEntityPydantic
from app.game_state.enums.resource import ResourceNodeVisibilityEnum

class ResourceNodeResourceEntityPydantic(BaseModel):
    """
    Entity representing a resource node.
    """
    resource_id: UUID
    is_primary: bool = True
    chance: float = 1.0
    amount_min: int = 1
    amount_max: int = 1
    purity: float = 1.0
    rarity: Optional[str] = "common"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    
    
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
    location_id: Optional[UUID] = None
    blueprint_id: Optional[UUID] = None
    theme_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    area_id: Optional[UUID] = None
    depleted: bool = False
    status: StatusEnum = StatusEnum.PENDING
    visibility: ResourceNodeVisibilityEnum = ResourceNodeVisibilityEnum.HIDDEN
    resource_links: List[ResourceNodeResourceEntityPydantic] = Field(default_factory=list)
    
    
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
                "visibility": "DISCOVERED",
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