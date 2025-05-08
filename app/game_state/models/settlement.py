# app/game_state/models/settlement.py

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

class SettlementEntity(BaseModel):
    id: Optional[UUID] = Field(None, alias="entity_id")
    name: str
    world_id: UUID
    description: Optional[str] = None
    population: int = 0
    buildings: List[Any] = []
    resources: List[Any] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
