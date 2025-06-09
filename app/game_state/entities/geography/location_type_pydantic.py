"""
Location type Pydantic entity representing the different types of locations in the game.
"""
from pydantic import Field, ConfigDict
from typing import Optional, List, Dict, Any

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class LocationTypeEntityPydantic(BaseEntityPydantic):
    """
    Pydantic entity representing a type of location.
    Each location type defines what kinds of locations it can contain
    and what attributes it requires.
    """
    
    # Type information
    code: Optional[str] = Field(None, description="Location type code (e.g., 'galaxy', 'star_system')")
    description: Optional[str] = Field(None, description="Description of the location type")
    theme: Optional[str] = Field(None, description="Theme associated with this location type")
    
    # Containment rules
    can_contain: List[str] = Field(default_factory=list, description="List of location type codes this can contain")
    
    # Attribute definitions
    required_attributes: List[Dict[str, Any]] = Field(default_factory=list, description="Required attributes for locations of this type")
    optional_attributes: List[Dict[str, Any]] = Field(default_factory=list, description="Optional attributes for locations of this type")
    
    # UI properties
    icon_path: Optional[str] = Field(None, description="Path to icon for this location type")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entity_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Star System",
                "code": "star_system",
                "description": "A star system containing planets and other celestial bodies",
                "theme": "space",
                "can_contain": ["planet", "asteroid_belt", "space_station"],
                "required_attributes": [
                    {"name": "star_type", "type": "string", "description": "Type of the primary star"}
                ],
                "optional_attributes": [
                    {"name": "hazard_level", "type": "integer", "description": "Danger level of the system"}
                ],
                "icon_path": "/icons/star_system.png"
            }
        }
    )
    
    def can_contain_type(self, type_code: str) -> bool:
        """Check if this location type can contain another type."""
        return type_code in self.can_contain
    
    def get_required_attribute_names(self) -> List[str]:
        """Get list of required attribute names."""
        return [attr.get("name") for attr in self.required_attributes if "name" in attr]
    
    def get_optional_attribute_names(self) -> List[str]:
        """Get list of optional attribute names."""
        return [attr.get("name") for attr in self.optional_attributes if "name" in attr]
    
    def validate_attributes(self, attributes: Dict[str, Any]) -> List[str]:
        """Validate that required attributes are present. Returns list of missing attributes."""
        required_names = self.get_required_attribute_names()
        missing = [name for name in required_names if name not in attributes]
        return missing