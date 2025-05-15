# --- START OF FILE app/game_state/entities/stat.py ---

import uuid
import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from .base import BaseEntity

# Define stat-specific enum
class StatCategory(enum.Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    DERIVED = "DERIVED"
    RESISTANCE = "RESISTANCE"
    COMBAT = "COMBAT"
    CRAFTING = "CRAFTING"

@dataclass
class StatEntity(BaseEntity):
    """
    Domain Entity representing a character or item stat.
    Inherits entity_id and name from BaseEntity.
    """
    # Stat values
    value: float = 0.0
    min_value: float = 0.0
    max_value: float = 100.0
    category: StatCategory = StatCategory.PRIMARY
    
    # Description and metadata
    description: Optional[str] = None
    modifier: Optional[float] = None
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Relationships
    owner_character_id: Optional[uuid.UUID] = None
    
    def __post_init__(self):
        """Validation and initialization."""
        if self.value < self.min_value:
            self.value = self.min_value
        elif self.value > self.max_value:
            self.value = self.max_value
            
        if self.updated_at is None:
            self.updated_at = self.created_at

# --- END OF FILE app/game_state/entities/stat.py ---