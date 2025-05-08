# --- START OF FILE app/game_state/models/world.py ---

"""
API Model (DTO) for World state
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class WorldEntity(BaseModel):
    """ world state DTO for API interactions """
    # Make ID optional for creation, but present for retrieval
    id: Optional[UUID] = Field(None, description="Unique identifier for the world")
    theme_id: Optional[UUID] = Field(None, description="Identifier for the world's theme") # Made optional for now, needs business logic decision
    name: str = Field(..., min_length=1, max_length=50, description="Name of the world")
    game_day: int = Field(..., ge=0, description="Current game day") # Changed from 'day' to match domain entity? Verify consistency.
    season: Optional[int] = Field(None, ge=0, description="Current season identifier (optional)") # Made optional
    size: Optional[int] = Field(None, ge=0, description="Size metric for the world (optional)") # Made optional
    created_at: Optional[datetime] = Field(None, description="Timestamp when the world was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the world was last updated")

    class Config:
        from_attributes = True

# --- END OF FILE app/game_state/models/world.py ---