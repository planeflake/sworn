from pydantic import Field, ConfigDict
from uuid import UUID
from typing import Optional, List, Dict, Any

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic
from app.game_state.enums.shared import StatusEnum, RarityEnum

class EquipmentEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing Equipment in the game.
    Inherits entity_id and name from BaseEntityPydantic.
    """
    # Primary attributes
    level: int = 1
    description: Optional[str] = None
    modifier: Optional[float] = None
    rarity: RarityEnum = RarityEnum.COMMON
    is_enabled: bool = True
    status: StatusEnum = StatusEnum.ACTIVE
    
    # Additional metadata - note tags are already in BaseEntityPydantic
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Relationships
    owner_character_id: Optional[UUID] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Steel Sword",
                "level": 3,
                "description": "A well-crafted steel sword",
                "modifier": 1.2,
                "rarity": "UNCOMMON",
                "is_enabled": True,
                "status": "ACTIVE",
                "tags": ["weapon", "melee", "sword"],
                "metadata": {
                    "damage_type": "slashing",
                    "min_damage": 5,
                    "max_damage": 10
                }
            }
        }
    )

# For backward compatibility
Equipment = EquipmentEntityPydantic