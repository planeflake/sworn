from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

from app.game_state.entities.action.character_action_pydantic import ActionType, ActionStatus

class CreateActionRequest(BaseModel):
    """Schema for creating a new character action."""
    
    name: str = Field(min_length=1, max_length=200, description="Human-readable name for the action")
    action_type: ActionType
    target_id: Optional[UUID] = Field(None, description="ID of target (resource node, blueprint, etc.)")
    location_id: UUID = Field(description="Location where action takes place")
    duration: Optional[int] = Field(None, gt=0, description="Duration in seconds (auto-calculated if not provided)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action-specific parameters")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Gather Iron Ore",
                    "action_type": "gather",
                    "target_id": "550e8400-e29b-41d4-a716-446655440001",
                    "location_id": "550e8400-e29b-41d4-a716-446655440002",
                    "parameters": {
                        "resource_type": "iron_ore",
                        "quantity": 5
                    }
                },
                {
                    "name": "Build House",
                    "action_type": "build",
                    "target_id": "550e8400-e29b-41d4-a716-446655440003",
                    "location_id": "550e8400-e29b-41d4-a716-446655440002",
                    "duration": 1800,
                    "parameters": {
                        "building_name": "My House",
                        "position": {"x": 10, "y": 15}
                    }
                }
            ]
        }
    )

class ActionResponse(BaseModel):
    """Schema for action API responses."""
    
    action_id: UUID = Field(alias="entity_id")
    name: str
    character_id: UUID
    action_type: ActionType
    target_id: Optional[UUID] = None
    location_id: UUID
    status: ActionStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: int
    progress: float = Field(ge=0.0, le=1.0)
    estimated_completion: Optional[datetime] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class UpdateActionRequest(BaseModel):
    """Schema for updating an existing action."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[ActionStatus] = None
    progress: Optional[float] = Field(None, ge=0.0, le=1.0)
    result: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": "completed",
                    "progress": 1.0,
                    "result": {
                        "resources_gathered": {
                            "iron_ore": 5
                        },
                        "experience_gained": 25
                    }
                }
            ]
        }
    )

class ActionListResponse(BaseModel):
    """Schema for listing multiple actions."""
    
    actions: List[ActionResponse]
    total: int
    active_count: int = Field(description="Number of active (queued/in-progress) actions")
    
    model_config = ConfigDict(from_attributes=True)