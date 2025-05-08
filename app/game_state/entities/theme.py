# --- START OF FILE app/game_state/entities/theme.py ---
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Optional

@dataclass
class Theme:
    """
    Represents a theme in the game (Domain Entity).
    """
    # Basic placeholder structure
    id: Optional[UUID] = field(default_factory=uuid4)
    name: str = "Default Theme" # Provide a default name
    description: Optional[str] = None
    # Add other relevant theme attributes like genre, style, etc.

    def __post_init__(self):
        # Ensure ID is set if default_factory was used and ID was None initially
        if self.id is None:
            self.id = uuid4()

# --- END OF FILE app/game_state/entities/theme.py ---