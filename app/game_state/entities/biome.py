# --- START OF FILE app/game_state/entities/biome.py ---

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from .base import BaseEntity

@dataclass(kw_only=True)
class BiomeEntity(BaseEntity):
    """
    Domain Entity representing a biome type in the game world.
    Biomes affect movement, danger levels, and resource availability.
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntity.
    """
    # --- Identifiers ---
    biome_id: str  # String identifier like 'plains', 'forest', etc.
    display_name: str  # User-friendly display name
    
    # --- Description ---
    description: Optional[str] = None
    
    # --- Gameplay Attributes ---
    base_movement_modifier: float = 1.0  # Movement speed multiplier (1.0 = normal)
    danger_level_base: int = 1  # Base danger level (1-5)
    resource_types: Dict[str, float] = field(default_factory=dict)  # Resource abundance multipliers
    
    # --- Visual Representation ---
    color_hex: Optional[str] = None  # Hexadecimal color code for map display
    icon_path: Optional[str] = None  # Path to biome icon image
    
    # --- Timestamps ---
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert BiomeEntity to a dictionary with safe serialization."""
        # Manually create dictionary instead of using as dict to avoid inheritance issues
        data = {
            "id": str(self.entity_id),
            "name": self.name,
            "biome_id": self.biome_id,
            "display_name": self.display_name,
            "description": self.description,
            "base_movement_modifier": self.base_movement_modifier,
            "danger_level_base": self.danger_level_base,
            "resource_types": self.resource_types,
            "color_hex": self.color_hex,
            "icon_path": self.icon_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        return data

# For backward compatibility
Biome = BiomeEntity

# --- END OF FILE app/game_state/entities/biome.py ---