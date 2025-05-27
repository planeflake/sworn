# --- START OF FILE app/game_state/entities/building.py ---

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# --- Project Imports ---
from ..base import BaseEntity # Import the BaseEntity

# --- Domain Entity Definition ---
@dataclass
class BuildingEntity(BaseEntity): # Inherit from BaseEntity
    """
    Domain Entity representing a building concept in the game world.
    This is different from BuildingInstanceEntity, which represents a specific constructed instance.
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntity.
    """
    # entity_id: uuid.UUID  (Inherited from BaseEntity)
    # name: str             (Inherited from BaseEntity)

    description: Optional[str] = None
    
    # --- Building Metadata ---
    type: str = "generic"
    category: str = "generic"
    tier: int = 1
    
    # --- Timestamps ---
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert BuildingEntity to a dictionary with safe serialization."""
        return {
            "id": str(self.entity_id),
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "category": self.category,
            "tier": self.tier,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

# For backward compatibility
Building = BuildingEntity

# --- END OF FILE app/game_state/entities/building.py ---