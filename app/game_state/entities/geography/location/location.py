"""
Location entity representing a location in the game world.
"""
from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.game_state.entities.base import BaseEntity
from app.game_state.entities.geography.location.location_reference import LocationReference
from app.game_state.entities.geography.location.location_type import LocationTypeEntity

@dataclass(kw_only=True)
class LocationEntity(BaseEntity):
    """
    Base class for all location types.
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with safe serialization."""
        data = super().to_dict()
        
        location_data = {
            "id": str(self.entity_id),
            "name": self.name,
            "location_type_id": str(self.location_type_id),
            "location_type_code": self.location_type.code if self.location_type else None,
            "parent_id": str(self.parent.location_id) if self.parent else None,
            "parent_type_id": str(self.parent.location_type_id) if self.parent else None,
            "description": self.description,
            "coordinates": self.coordinates,
            "attributes": self.attributes,
            "is_active": self.is_active
        }
        
        data.update(location_data)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LocationEntity":
        """Create from dictionary."""
        # Handle parent reference
        parent = None
        if data.get("parent_id") and data.get("parent_type_id"):
            parent = LocationReference(
                location_id=UUID(data["parent_id"]),
                location_type_id=UUID(data["parent_type_id"]),
                location_type_code=data.get("parent_type_code")
            )
        
        # Create location entity
        return cls(
            entity_id=UUID(data["id"]) if "id" in data and data["id"] else None,
            name=data["name"],
            location_type_id=UUID(data["location_type_id"]),
            parent=parent,
            description=data.get("description"),
            coordinates=data.get("coordinates", {}),
            attributes=data.get("attributes", {}),
            tags=data.get("tags", []),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Safely get an attribute value."""
        return self.attributes.get(key, default)
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute value."""
        self.attributes[key] = value
        
    def has_attribute(self, key: str) -> bool:
        """Check if an attribute exists."""
        return key in self.attributes