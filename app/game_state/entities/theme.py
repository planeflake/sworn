from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.game_state.entities.base import BaseEntity

@dataclass(kw_only=True)
class ThemeEntity(BaseEntity):
    """
    Represents a theme in the game (e.g., Fantasy, Sci-Fi, Post-Apocalyptic).
    Used to classify worlds, currencies, factions, etc.
    """

    # --- Theme-specific fields ---
    description: Optional[str] = None
    genre: Optional[str] = None       # e.g., "Fantasy", "Cyberpunk"
    style: Optional[str] = None       # e.g., "Steampunk", "Noir"
    
    # Override the default name for themes
    name: str = "Default Theme"

    def to_dict(self) -> Dict[str, Any]:
        """Convert ThemeEntity to a dictionary with safe serialization."""
        # Get base entity fields
        data = super().to_dict()
        
        # Add theme-specific fields
        theme_data = {
            "description": self.description,
            "genre": self.genre,
            "style": self.style,
            # Add id for database/API compatibility
            "id": str(self.entity_id)
        }
            
        data.update(theme_data)
        return data

# For backward compatibility
Theme = ThemeEntity