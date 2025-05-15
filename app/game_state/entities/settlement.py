# settlement.py
from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, List, Any, Dict
from datetime import datetime
# Import the base entity
from app.game_state.entities.base import BaseEntity

@dataclass
class SettlementEntity(BaseEntity):
    """
    Represents a Settlement in the game (Domain Entity).
    Inherits entity_id and name as fields from BaseEntity.
    """
    # --- Fields with defaults ---
    world_id: UUID = None
    leader_id: Optional[UUID] = None
    description: Optional[str] = None
    buildings: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    population: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert SettlementEntity to a dictionary with safe serialization."""
        # Manually create dictionary instead of using asdict to avoid inheritance issues
        data = {
            "id": str(self.entity_id),
            "name": self.name,
            "world_id": str(self.world_id) if self.world_id else None,
            "leader_id": str(self.leader_id) if self.leader_id else None,
            "description": self.description,
            "buildings": self.buildings,
            "resources": self.resources,
            "population": self.population,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        return data

# For backward compatibility
Settlement = SettlementEntity