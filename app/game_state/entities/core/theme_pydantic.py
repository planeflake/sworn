from pydantic import Field, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class ThemeEntityPydantic(BaseEntityPydantic):
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
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Fantasy Theme",
                "description": "A high fantasy medieval setting",
                "genre": "Fantasy",
                "style": "Medieval"
            }
        }
    )

# For backward compatibility if needed
Theme = ThemeEntityPydantic