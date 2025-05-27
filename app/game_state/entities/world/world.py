from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Optional, List, Any, Dict
from datetime import datetime

from app.game_state.entities.core.base import BaseEntity

@dataclass
class WorldEntity(BaseEntity):
    """
    Represents a world in the game (Domain Entity).
    Inherits entity_id, name, timestamps, tags, and _metadata from BaseEntity.
    """
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
    # created_at, updated_at, tags, and _metadata are now inherited from BaseEntity

    def __post_init__(self):
        # Call the parent's post init if it exists
        if hasattr(super(), '__post_init__'):
            super().__post_init__()

    def to_dict(self) -> Dict[str, Any]:
        """Convert WorldEntity to a dictionary with safe serialization."""
        # Get base entity fields first
        data = super().to_dict()
        
        # For backward compatibility, add id field as alias for entity_id
        data["id"] = data["entity_id"]
        
        # Add world-specific fields
        world_data = {
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
        }
        
        # Update with world-specific data
        data.update(world_data)
        
        # Handle complex nested objects
        if hasattr(self, 'settlements') and self.settlements:
            data['settlements'] = [settlement.to_dict() if hasattr(settlement, 'to_dict') else settlement 
                                  for settlement in self.settlements]
        
        return data

# For backward compatibility
World = WorldEntity