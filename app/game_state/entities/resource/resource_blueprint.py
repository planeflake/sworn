# --- START OF FILE app/game_state/entities/resources/resource_blueprint.py ---

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ResourceBlueprintEntity(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    theme_id: Optional[uuid.UUID] = None
    rarity: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceBlueprintEntity":
        return cls(**data)
