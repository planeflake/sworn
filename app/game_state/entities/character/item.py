# --- START OF FILE app/game_state/entities/item.py ---

import uuid
import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from ..base import BaseEntity
from app.game_state.enums.shared import StatusEnum, RarityEnum

# Equipment slots enum
class ItemSlot(enum.Enum):
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

@dataclass
class ItemEntity(BaseEntity):
    """
    Domain Entity representing an item in the game.
    Inherits entity_id and name from BaseEntity.
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
    for_sale_at: Optional[uuid.UUID] = None # Shop/Market ID
    buy_price: Optional[float] = None
    sell_price: Optional[float] = None
    
    # Additional game mechanics
    requirements: Dict[str, Any] = field(default_factory=dict)
    effects: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert ItemEntity to a dictionary with safe serialization."""
        # Manually create dictionary instead of using asdict to avoid inheritance issues
        data = {
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
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        return data

# For backward compatibility
Item = ItemEntity

# --- END OF FILE app/game_state/entities/item.py ---