# --- START OF FILE app/game_state/entities/zone_routes.py ---

# --- Core Python Imports ---
from uuid import UUID
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any # For type hinting

# --- Project Imports ---
from app.game_state.enums.shared import StatusEnum
from ..base import BaseEntity    # Import the BaseEntity


# --- Domain Entity Definition ---
@dataclass(kw_only=True)
class Zone(BaseEntity): # Inherit from BaseEntity
    """
    Zone entity representing a geographical area in the game world.
    Inherits 'entity_id' and 'name' from BaseEntity.
    Zones are areas within a world that can contain settlements, resources, and NPCs.

    NOTE: Inherited fields:
     - entity_id: UUID (from BaseEntity)
     - name: str (from BaseEntity, defaults to "Unnamed Entity")
     - created_at: datetime
     - updated_at: Optional[datetime]
     - tags: List[str]
     - _metadata: Dict[str, Any]
    """

    # --- Specific Attributes for this Entity ---
    # Optional longer text description
    description: Optional[str] = None
    
    # Foreign keys to other entities
    world_id: UUID = None  # Required: The world this zone belongs to
    theme_id: Optional[UUID] = None  # Optional: The primary theme of this zone
    controlling_faction: Optional[UUID] = None  # Optional: The faction controlling this zone
    
    # Collections of related entity IDs
    settlements: List[UUID] = field(default_factory=list)
    areas: List[UUID] = field(default_factory=list)  # Areas within this zone
    biomes: List[UUID] = field(default_factory=list)
    
    # Status and other properties
    status: StatusEnum = StatusEnum.ACTIVE

    def __post_init__(self):
        """
        Called automatically after the dataclass is initialized.
        Ensures the parent class __post_init__ is called if it exists.
        """
        if hasattr(super(), '__post_init__'):
            super().__post_init__()

    def to_dict(self) -> Dict[str, Any]:
        """Convert Zone entity to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add zone-specific fields
        zone_data = {
            "id": str(self.entity_id),  # For database/API compatibility
            "description": self.description,
            "world_id": str(self.world_id) if self.world_id else None,
            "theme_id": str(self.theme_id) if self.theme_id else None,
            "controlling_faction": str(self.controlling_faction) if self.controlling_faction else None,
            "settlements": [str(s) for s in self.settlements],
            "areas": [str(a) for a in self.areas],
            "biomes": [str(b) for b in self.biomes],
            "status": self.status.value,
        }
        
        data.update(zone_data)
        return data

# For backward compatibility
ZoneEntity = Zone

# --- END OF FILE app/game_state/entities/zone_routes.py ---