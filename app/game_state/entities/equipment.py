# --- START OF FILE app/game_state/entities/equipment.py ---

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from .base import BaseEntity
from app.game_state.enums.shared import StatusEnum, RarityEnum

@dataclass
class EquipmentEntity(BaseEntity):
    """
    Domain Entity representing Equipment in the game.
    Inherits entity_id and name from BaseEntity.
    """
    # Primary attributes
    level: int = 1
    description: Optional[str] = None
    modifier: Optional[float] = None
    rarity: RarityEnum = RarityEnum.COMMON
    is_enabled: bool = True
    status: StatusEnum = StatusEnum.ACTIVE
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Relationships
    owner_character_id: Optional[uuid.UUID] = None
    
    def __post_init__(self):
        """Initialize updated_at if needed."""
        if self.updated_at is None:
            self.updated_at = self.created_at

# --- END OF FILE app/game_state/entities/equipment.py ---