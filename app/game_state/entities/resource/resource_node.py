# --- START OF FILE app/game_state/entities/resource_node.py ---

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.game_state.enums.shared import StatusEnum

class ResourceNodeResourceEntity(BaseModel):
    resource_id: uuid.UUID
    is_primary: bool = True
    chance: float = 1.0
    amount_min: int = 1
    amount_max: int = 1
    purity: float = 1.0
    rarity: Optional[str] = "common"
    _metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceNodeResourceEntity":
        return cls(**data)


class ResourceNodeEntity(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    blueprint_id: Optional[uuid.UUID] = None
    theme_id: Optional[uuid.UUID] = None
    zone_id: Optional[uuid.UUID] = None
    area_id: Optional[uuid.UUID] = None
    depleted: bool = False
    status: StatusEnum = StatusEnum.PENDING
    _metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    resource_links: List[ResourceNodeResourceEntity] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceNodeEntity":
        return cls(**data)