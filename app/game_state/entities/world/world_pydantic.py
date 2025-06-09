from pydantic import Field, ConfigDict
from uuid import UUID
from typing import Optional, List, Any

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class WorldEntityPydantic(BaseEntityPydantic):
    """
    Represents a world in the game (Domain Entity).
    Inherits entity_id, name, timestamps, tags, and metadata from BaseEntityPydantic.
    """
    theme_id: Optional[UUID] = None
    day: int = 0
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