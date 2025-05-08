# --- START OF FILE app/game_state/entities/world.py ---
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Optional, List,Any
# from .base import BaseEntity # Assuming BaseEntity exists and handles name/id if needed

@dataclass
class World: # Removed inheritance temporarily for simplicity, add back if BaseEntity is simple
    """
    Represents a world in the game (Domain Entity).
    Uses dataclass fields for initialization.
    """
    name: str
    id: UUID = field(default_factory=uuid4) # Let factory create ID
    theme_id: Optional[UUID] = None # Default theme_id is None until set
    game_day: int = 0
    size: Optional[int] = None
    climate: Optional[str] = None # Assuming climate is a string
    description: Optional[str] = None
    settlements: List[Any] = field(default_factory=list) # Replace Any with specific type
    resources: List[Any] = field(default_factory=list)
    factions: List[Any] = field(default_factory=list)
    events: List[Any] = field(default_factory=list)
    npcs: List[Any] = field(default_factory=list)
    quests: List[Any] = field(default_factory=list)
    season: Optional[int] = None # Assuming season is an int
    celestial_bodies: List[Any] = field(default_factory=list)
    weather: Optional[str] = None # Assuming weather is a string
    population: int = 0
    dungeons: List[Any] = field(default_factory=list)

    # Removed custom __init__ and __tablename__

    def __post_init__(self):
        # Ensure ID is set if factory wasn't used somehow (defensive)
        if self.id is None:
            self.id = uuid4()
        # You might add other post-init logic here if needed

# --- END OF FILE app/game_state/entities/world.py ---