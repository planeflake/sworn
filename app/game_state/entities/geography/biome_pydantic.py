from uuid import UUID

from pydantic import Field, ConfigDict
from typing import Optional, Dict, List

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
    theme_ids: List[UUID] = Field(
        default_factory=list,
        description="Theme IDs this biome belongs to"
    )
    # --- Visual Representation ---
    color_hex: Optional[str] = None  # Hexadecimal color code for map display
    icon_path: Optional[str] = None  # Path to biome icon image
    

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
                "themes": ["b2494b91-f7d1-4c8d-9da2-c628816ed9de","1265b705-778e-4df1-b7ac-2a3f7a01ac22"],
                "color_hex": "#228B22"
            }
        }
    )

# For backward compatibility
Biome = BiomeEntityPydantic