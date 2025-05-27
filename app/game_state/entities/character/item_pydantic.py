from pydantic import Field, ConfigDict
from uuid import UUID
from typing import Optional, Dict, Any
from enum import Enum

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic
from app.game_state.enums.shared import StatusEnum, RarityEnum

# Equipment slots enum - keeping the same enum from the original file
class ItemSlot(Enum):
    # Armor slots
    HEAD = "HEAD"
    SHOULDERS = "SHOULDERS"
    CHEST = "CHEST"
    HANDS = "HANDS" 
    WRISTS = "WRISTS"
    WAIST = "WAIST"
    LEGS = "LEGS"
    FEET = "FEET"
    
    # Weapon/accessory slots
    MAIN_HAND = "MAIN_HAND"
    OFF_HAND = "OFF_HAND"
    RANGED = "RANGED"
    NECK = "NECK"
    FINGER1 = "FINGER1"
    FINGER2 = "FINGER2"
    TRINKET1 = "TRINKET1"
    TRINKET2 = "TRINKET2"
    CLOAK = "CLOAK"
    
    # Non-equipment items 
    NONE = "NONE"  # General inventory items that aren't equippable

class ItemEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing an item in the game.
    Inherits entity_id and name from BaseEntityPydantic.
    """
    # Item attributes
    description: Optional[str] = None 
    slot: ItemSlot = ItemSlot.NONE
    quantity: int = 1
    weight: float = 0.0
    value: float = 0.0
    is_stackable: bool = False
    is_tradable: bool = True
    
    # Item quality and status
    status: StatusEnum = StatusEnum.ACTIVE
    rarity: RarityEnum = RarityEnum.COMMON
    
    # Market information
    for_sale_at: Optional[UUID] = None # Shop/Market ID
    buy_price: Optional[float] = None
    sell_price: Optional[float] = None
    
    # Additional game mechanics
    requirements: Dict[str, Any] = Field(default_factory=dict)
    effects: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ItemEntity to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add item-specific fields
        item_data = {
            "id": str(self.entity_id),
            "name": self.name,
            "description": self.description,
            "slot": self.slot.value,
            "quantity": self.quantity,
            "weight": self.weight,
            "value": self.value,
            "is_stackable": self.is_stackable,
            "is_tradable": self.is_tradable,
            "status": self.status.value,
            "rarity": self.rarity.value,
            "for_sale_at": str(self.for_sale_at) if self.for_sale_at else None,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "requirements": self.requirements,
            "effects": self.effects,
        }
        
        data.update(item_data)
        return data
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Health Potion",
                "description": "Restores 50 health points when consumed",
                "slot": "NONE",
                "quantity": 5,
                "weight": 0.2,
                "value": 25.0,
                "is_stackable": True,
                "is_tradable": True,
                "status": "ACTIVE",
                "rarity": "COMMON",
                "effects": {
                    "heal": 50,
                    "duration": "instant"
                }
            }
        }
    )

# For backward compatibility
Item = ItemEntityPydantic