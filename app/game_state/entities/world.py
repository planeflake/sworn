# --- START OF FILE app/game_state/entities/world.py ---
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Optional, List, Any, Dict
from datetime import datetime

@dataclass
class WorldEntity:
    """
    Represents a world in the game (Domain Entity).
    Uses dataclass fields for initialization.
    """
    name: str
    id: UUID = field(default_factory=uuid4)
    theme_id: Optional[UUID] = None
    day: int = 0  # Renamed from game_day to match API schema
    size: Optional[int] = None
    climate: Optional[str] = None
    description: Optional[str] = None
    settlements: List[Any] = field(default_factory=list)
    resources: List[Any] = field(default_factory=list)
    factions: List[Any] = field(default_factory=list)
    events: List[Any] = field(default_factory=list)
    npcs: List[Any] = field(default_factory=list)
    quests: List[Any] = field(default_factory=list)
    season: Optional[int] = None
    celestial_bodies: List[Any] = field(default_factory=list)
    weather: Optional[str] = None
    population: int = 0
    dungeons: List[Any] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # Ensure ID is set if factory wasn't used somehow (defensive)
        if self.id is None:
            self.id = uuid4()
        
        # Set created_at if not provided
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert WorldEntity to a dictionary with safe serialization."""
        # Manually create dictionary instead of using asdict to avoid inheritance issues
        data = {
            "id": str(self.id),
            "name": self.name,
            "theme_id": str(self.theme_id) if self.theme_id else None,
            "day": self.day,
            "size": self.size,
            "climate": self.climate,
            "description": self.description,
            "settlements": self.settlements,
            "resources": self.resources,
            "factions": self.factions,
            "events": self.events,
            "npcs": self.npcs,
            "quests": self.quests,
            "season": self.season,
            "celestial_bodies": self.celestial_bodies,
            "weather": self.weather,
            "population": self.population,
            "dungeons": self.dungeons,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Handle complex nested objects if needed
        # For example, if settlements contains custom objects with to_dict:
        # data['settlements'] = [settlement.to_dict() if hasattr(settlement, 'to_dict') else settlement 
        #                        for settlement in self.settlements]
        
        return data

# For backward compatibility
World = WorldEntity

# --- END OF FILE app/game_state/entities/world.py ---