from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from datetime import datetime, UTC

@dataclass(kw_only=True)
class ThemeEntity:
    """
    Represents a theme in the game (e.g., Fantasy, Sci-Fi, Post-Apocalyptic).
    Used to classify worlds, currencies, factions, etc.
    """

    # --- Core Identity ---
    id: UUID = field(default_factory=uuid4)
    name: str = "Default Theme"
    description: Optional[str] = None

    # --- Optional Metadata ---
    genre: Optional[str] = None       # e.g., "Fantasy", "Cyberpunk"
    style: Optional[str] = None       # e.g., "Steampunk", "Noir"
    tags: List[str] = field(default_factory=list)

    # --- Timestamps ---
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.id is None:
            self.id = uuid4()

    def to_dict(self) -> Dict[str, Any]:
        """Convert ThemeEntity to a dictionary with safe serialization."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "genre": self.genre,
            "style": self.style,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

# For backward compatibility
Theme = ThemeEntity