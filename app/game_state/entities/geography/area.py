# area.py
from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.game_state.enums.shared import StatusEnum
from ..base import BaseEntity  # Import the BaseEntity

@dataclass(kw_only=True)
class Area(BaseEntity):
    """
    Area entity representing a specific location within a Zone.
    Inherits 'entity_id' and 'name' from BaseEntity.
    Areas are sub-sections of a Zone that can contain settlements, resources, and NPCs.

    NOTE: Inherited fields:
     - entity_id: UUID (from BaseEntity)
     - name: str (from BaseEntity, defaults to "Unnamed Entity")
     - created_at: datetime
     - updated_at: Optional[datetime]
     - tags: List[str]
     - metadata: Dict[str, Any]
    """

    # --- Specific Attributes for this Entity ---
    # Optional longer text description
    description: Optional[str] = None
    
    # Foreign keys to other entities
    zone_id: UUID = None  # Required: The zone this area belongs to
    world_id: UUID = None  # Required: The world this area belongs to (inherited from zone)
    biome_id: Optional[UUID] = None  # Optional: The primary biome of this area
    theme_id: Optional[UUID] = None  # Optional: The primary theme of this area
    controlling_faction: Optional[UUID] = None  # Optional: The faction controlling this area
    
    # Geographical properties
    size: float = 1.0  # Size in square kilometers
    coordinates: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0})  # Location coordinates
    elevation: float = 0.0  # Elevation in meters
    
    # Collections of related entity IDs
    settlement_ids: List[UUID] = field(default_factory=list)  # Settlements in this area
    resource_node_ids: List[UUID] = field(default_factory=list)  # Resource nodes in this area
    character_ids: List[UUID] = field(default_factory=list)  # Characters in this area
    
    # Status and other properties
    status: StatusEnum = StatusEnum.ACTIVE
    is_discovered: bool = False  # Whether the area has been discovered by players
    danger_level: int = 0  # How dangerous the area is (0-10)

    def __post_init__(self):
        """
        Called automatically after the dataclass is initialized.
        Ensures the parent class __post_init__ is called if it exists.
        """
        if hasattr(super(), '__post_init__'):
            super().__post_init__()

    def to_dict(self) -> Dict[str, Any]:
        """Convert Area entity to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add area-specific fields
        area_data = {
            "id": str(self.entity_id),  # For database/API compatibility
            "description": self.description,
            "zone_id": str(self.zone_id) if self.zone_id else None,
            "world_id": str(self.world_id) if self.world_id else None,
            "biome_id": str(self.biome_id) if self.biome_id else None,
            "theme_id": str(self.theme_id) if self.theme_id else None,
            "controlling_faction": str(self.controlling_faction) if self.controlling_faction else None,
            "size": self.size,
            "coordinates": self.coordinates,
            "elevation": self.elevation,
            "settlement_ids": [str(s) for s in self.settlement_ids],
            "resource_node_ids": [str(r) for r in self.resource_node_ids],
            "character_ids": [str(c) for c in self.character_ids],
            "status": self.status.value,
            "is_discovered": self.is_discovered,
            "danger_level": self.danger_level,
        }
        
        data.update(area_data)
        return data

    def add_settlement(self, settlement_id: UUID) -> None:
        """
        Add a settlement to this area.
        
        Args:
            settlement_id: UUID of the settlement to add
        """
        if settlement_id not in self.settlement_ids:
            self.settlement_ids.append(settlement_id)

    def remove_settlement(self, settlement_id: UUID) -> bool:
        """
        Remove a settlement from this area.
        
        Args:
            settlement_id: UUID of the settlement to remove
            
        Returns:
            True if settlement was successfully removed, False if not found
        """
        if settlement_id in self.settlement_ids:
            self.settlement_ids.remove(settlement_id)
            return True
        return False

    def add_resource_node(self, resource_node_id: UUID) -> None:
        """
        Add a resource node to this area.
        
        Args:
            resource_node_id: UUID of the resource node to add
        """
        if resource_node_id not in self.resource_node_ids:
            self.resource_node_ids.append(resource_node_id)

    def remove_resource_node(self, resource_node_id: UUID) -> bool:
        """
        Remove a resource node from this area.
        
        Args:
            resource_node_id: UUID of the resource node to remove
            
        Returns:
            True if resource node was successfully removed, False if not found
        """
        if resource_node_id in self.resource_node_ids:
            self.resource_node_ids.remove(resource_node_id)
            return True
        return False

# For backward compatibility
AreaEntity = Area