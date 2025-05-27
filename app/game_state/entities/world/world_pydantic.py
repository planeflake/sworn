from pydantic import Field, ConfigDict
from uuid import UUID
from typing import Optional, List, Any, Dict

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class WorldEntityPydantic(BaseEntityPydantic):
    """
    Represents a world in the game (Domain Entity).
    Inherits entity_id, name, timestamps, tags, and metadata from BaseEntityPydantic.
    """
    theme_id: Optional[UUID] = None
    day: int = 0  # Renamed from game_day to match API schema
    size: Optional[int] = None
    climate: Optional[str] = None
    description: Optional[str] = None
    settlements: List[Any] = Field(default_factory=list)
    resources: List[Any] = Field(default_factory=list)
    factions: List[Any] = Field(default_factory=list)
    events: List[Any] = Field(default_factory=list)
    npcs: List[Any] = Field(default_factory=list)
    quests: List[Any] = Field(default_factory=list)
    season: Optional[int] = None
    celestial_bodies: List[Any] = Field(default_factory=list)
    weather: Optional[str] = None
    population: int = 0
    dungeons: List[Any] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert WorldEntity to a dictionary with safe serialization."""
        # Get base entity fields
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
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Eldoria",
                "theme_id": "550e8400-e29b-41d4-a716-446655440000",
                "day": 42,
                "size": 1000,
                "climate": "Temperate",
                "description": "A fantasy world with diverse biomes and ancient magic",
                "population": 10000,
                "season": 2,
                "weather": "Rainy"
            }
        }
    )

# For backward compatibility
World = WorldEntityPydantic