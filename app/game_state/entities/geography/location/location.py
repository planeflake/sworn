"""
Location entity representing a location in the game world.
"""
from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, Dict, Any

from app.game_state.entities.base import BaseEntity
from app.game_state.entities.geography.location.location_reference import LocationReference
from app.game_state.entities.geography.location.location_type import LocationTypeEntity

class LocationEntity(BaseEntity):
    """
    Base class for all location.
    Each location has a type that defines its properties and behavior.
    """
    
    # Location type
    location_type_id: UUID
    location_type: Optional[LocationTypeEntity] = None  # Full type entity when needed
    
    # Parent reference
    parent: Optional[LocationReference] = None
    
    # Common attributes
    description: Optional[str] = None
    coordinates: Dict[str, float] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

    # Unique attributes
    world_id: UUID = field(default_factory=lambda: UUID(int=0))
    biome_id: UUID = field(default_factory=lambda: UUID(int=0))
    theme_id: UUID = field(default_factory=lambda: UUID(int=0))
    base_danger_level = int
    controlling_faction_id: Optional[UUID] = None


    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Safely get an attribute value."""
        return self.attributes.get(key, default)
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute value."""
        self.attributes[key] = value
        
    def has_attribute(self, key: str) -> bool:
        """Check if an attribute exists."""
        return key in self.attributes