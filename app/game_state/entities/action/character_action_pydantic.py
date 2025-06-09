from pydantic import Field, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class ActionType(str, Enum):
    GATHER = "gather"
    BUILD = "build"
    CRAFT = "craft"
    TRADE = "trade"
    MOVE = "move"
    REST = "rest"

class ActionStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CharacterActionPydantic(BaseEntityPydantic):
    """Pure data entity for character actions - inherits from your BaseEntityPydantic."""
    
    # Required fields
    character_id: UUID
    action_type: ActionType
    location_id: UUID
    duration: int = Field(gt=0, description="Duration in seconds")
    
    # Optional fields
    target_id: Optional[UUID] = None
    status: ActionStatus = ActionStatus.QUEUED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Gather Iron Ore",
                "character_id": "550e8400-e29b-41d4-a716-446655440000",
                "action_type": "gather",
                "target_id": "550e8400-e29b-41d4-a716-446655440001", 
                "location_id": "550e8400-e29b-41d4-a716-446655440002",
                "duration": 300,
                "parameters": {
                    "resource_type": "iron_ore",
                    "quantity": 5
                }
            }
        }
    )

# For backward compatibility and consistency with your pattern
CharacterAction = CharacterActionPydantic