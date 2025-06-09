from pydantic import ConfigDict, computed_field
from typing import Optional

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic
from app.game_state.enums.theme import Genre

class ThemeEntityPydantic(BaseEntityPydantic):
    """
    Represents a theme in the game (e.g., Fantasy, Sci-Fi, Post-Apocalyptic).
    Used to classify worlds, currencies, factions, etc.
    """

    # --- Theme-specific fields ---
    description: Optional[str] = None
    genre: Genre = Genre.FANTASY       # e.g., "Fantasy", "Cyberpunk"
    style: Optional[str] = None       # e.g., "Steampunk", "Noir"
    
    # Override the default name for themes
    name: str = "Default Theme"

    @computed_field
    @property
    def fullname(self) -> str:
        """Full name with genre in brackets."""
        if self.genre:
            genre_display = self.genre.value.replace('_', ' ').title()
            return f"{self.name} ({genre_display})"
        else:
            return self.name

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Fantasy Theme",
                "description": "A high fantasy medieval setting",
                "genre": "fantasy",
                "style": "Medieval"
            }
        }
    )

# For backward compatibility if needed
Theme = ThemeEntityPydantic