"""
DEPRECATED: This model is being phased out in favor of using app.game_state.entities.settlement.Settlement directly.
Use app.game_state.entities.settlement.Settlement for new code.
"""
import warnings
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

warnings.warn(
    "SettlementEntity is deprecated, use app.game_state.entities.settlement.Settlement instead",
    DeprecationWarning,
    stacklevel=2
)

class SettlementEntity(BaseModel):
    """
    DEPRECATED: Use app.game_state.entities.settlement.Settlement instead.
    This class is maintained for backward compatibility during transition.
    """
    id: Optional[UUID] = Field(None, alias="entity_id")
    name: str
    world_id: UUID
    description: Optional[str] = None
    population: int = 0
    buildings: List[Any] = []
    resources: List[Any] = []
    leader_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        warnings.warn(
            "SettlementEntity is deprecated, use app.game_state.entities.settlement.Settlement instead",
            DeprecationWarning,
            stacklevel=2
        )
    
    class Config:
        populate_by_name = True