"""
Location type entity representing the different types of locations in the game.
"""
from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.game_state.entities.base import BaseEntity

@dataclass(kw_only=True)
class LocationTypeEntity(BaseEntity):
    """
    Entity representing a type of location.
    Each location type defines what kinds of locations it can contain
    and what attributes it requires.
    """
    
    # Type information
    code: str  # e.g., 'galaxy', 'star_system'
    description: Optional[str] = None
    theme: Optional[str] = None
    
    # Containment rules
    can_contain: List[str] = field(default_factory=list)
    
    # Attribute definitions
    required_attributes: List[Dict[str, Any]] = field(default_factory=list)
    optional_attributes: List[Dict[str, Any]] = field(default_factory=list)
    
    # UI properties
    icon_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with safe serialization."""
        data = super().to_dict()
        
        type_data = {
            "id": str(self.entity_id),
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "theme": self.theme,
            "can_contain": self.can_contain,
            "required_attributes": self.required_attributes,
            "optional_attributes": self.optional_attributes,
            "icon_path": self.icon_path
        }
        
        data.update(type_data)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LocationTypeEntity":
        """Create from dictionary."""
        return cls(
            entity_id=UUID(data["id"]) if "id" in data and data["id"] else None,
            code=data["code"],
            name=data["name"],
            description=data.get("description"),
            theme=data.get("theme"),
            can_contain=data.get("can_contain", []),
            required_attributes=data.get("required_attributes", []),
            optional_attributes=data.get("optional_attributes", []),
            icon_path=data.get("icon_path"),
            tags=data.get("tags", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def can_contain_type(self, type_code: str) -> bool:
        """Check if this location type can contain another type."""
        return type_code in self.can_contain