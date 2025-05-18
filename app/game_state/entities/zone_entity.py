from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from app.game_state.entities.base import BaseEntity
from app.game_state.enums.shared import StatusEnum
from app.db.models.zone import ZonalStateEnum

class ZoneEntity(BaseEntity):
    """
    Entity representing a geographical zone in the game world.
    Zones are areas that contain settlements, resources, and other game elements.
    They have specific biomes and themes that influence gameplay.
    """
    def __init__(
        self,
        id: Union[UUID, str],
        name: str,
        description: Optional[str],
        controlling_faction: Optional[UUID],
        state: ZonalStateEnum,
        status: StatusEnum,
        world_id: UUID,
        biome_id: UUID,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        _metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(id)
        self.name = name
        self.description = description
        self.controlling_faction = controlling_faction
        self.state = state
        self.status = status
        self.world_id = world_id
        self.biome_id = biome_id
        self.created_at = created_at
        self.updated_at = updated_at
        self._metadata = _metadata or {}
        self.tags = tags or []
        
        # Related entities
        self.world = None
        self.biome = None
        self.settlements = []
        self.themes = []
        
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to a dictionary representation"""
        data = {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "controlling_faction": str(self.controlling_faction) if self.controlling_faction else None,
            "state": self.state.value if self.state else None,
            "status": self.status.value if self.status else None,
            "world_id": str(self.world_id) if self.world_id else None,
            "biome_id": str(self.biome_id) if self.biome_id else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self._metadata,
            "tags": self.tags,
            "world": self.world.to_dict() if self.world and hasattr(self.world, 'to_dict') else None,
            "biome": self.biome.to_dict() if self.biome and hasattr(self.biome, 'to_dict') else None,
            "settlements": [s.to_dict() if hasattr(s, 'to_dict') else s for s in self.settlements] if self.settlements else [],
            "themes": [t.to_dict() if hasattr(t, 'to_dict') else t for t in self.themes] if self.themes else [],
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ZoneEntity":
        """Create entity from dictionary data"""
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            controlling_faction=UUID(data.get("controlling_faction")) if data.get("controlling_faction") else None,
            state=ZonalStateEnum(data.get("state")) if data.get("state") else ZonalStateEnum.PEACEFUL,
            status=StatusEnum(data.get("status")) if data.get("status") else StatusEnum.ACTIVE,
            world_id=UUID(data.get("world_id")) if data.get("world_id") else None,
            biome_id=UUID(data.get("biome_id")) if data.get("biome_id") else None,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            _metadata=data.get("metadata"),
            tags=data.get("tags"),
        )