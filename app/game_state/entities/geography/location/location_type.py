"""
Location type entity representing the different types of locations in the game.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

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

    def can_contain_type(self, type_code: str) -> bool:
        """Check if this location type can contain another type."""
        return type_code in self.can_contain