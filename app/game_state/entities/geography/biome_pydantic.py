from pydantic import Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class BiomeEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing a biome type in the game world.
    Biomes affect movement, danger levels, and resource availability.
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntityPydantic.
    """
    # --- Identifiers ---
    biome_id: str  # String identifier like 'plains', 'forest', etc.
    display_name: str  # User-friendly display name
    
    # --- Description ---
    description: Optional[str] = None
    
    # --- Gameplay Attributes ---
    base_movement_modifier: float = 1.0  # Movement speed multiplier (1.0 = normal)
    danger_level_base: int = 1  # Base danger level (1-5)
    resource_types: Dict[str, float] = Field(default_factory=dict)  # Resource abundance multipliers
    
    # --- Visual Representation ---
    color_hex: Optional[str] = None  # Hexadecimal color code for map display
    icon_path: Optional[str] = None  # Path to biome icon image
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert BiomeEntity to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add biome-specific fields
        biome_data = {
            "biome_id": self.biome_id,
            "display_name": self.display_name,
            "description": self.description,
            "base_movement_modifier": self.base_movement_modifier,
            "danger_level_base": self.danger_level_base,
            "resource_types": self.resource_types,
            "color_hex": self.color_hex,
            "icon_path": self.icon_path,
            # Add id for database/API compatibility
            "id": str(self.entity_id)
        }
            
        data.update(biome_data)
        return data
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Forest",
                "biome_id": "forest",
                "display_name": "Dense Forest",
                "description": "A lush, dense forest with tall trees and abundant wildlife",
                "base_movement_modifier": 0.8,
                "danger_level_base": 2,
                "resource_types": {
                    "wood": 1.5,
                    "herbs": 1.2,
                    "stone": 0.5
                },
                "color_hex": "#228B22"
            }
        }
    )

# For backward compatibility
Biome = BiomeEntityPydantic