"""
DEPRECATED: This model is being phased out in favor of using app.game_state.entities.world.World directly.
Use app.game_state.entities.world.World for domain logic and app.api.schemas.world for API validation.
"""
import warnings
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

warnings.warn(
    "WorldEntity is deprecated, use app.game_state.entities.world.World for domain logic and "
    "app.api.schemas.world for API validation",
    DeprecationWarning,
    stacklevel=2
)

class WorldEntity(BaseModel):
    """
    DEPRECATED: Use app.game_state.entities.world.World and app.api.schemas.world instead.
    This class is maintained for backward compatibility during transition.
    """
    # Make ID optional for creation, but present for retrieval
    id: Optional[UUID] = Field(None, description="Unique identifier for the world")
    theme_id: Optional[UUID] = Field(None, description="Identifier for the world's theme")
    name: str = Field(..., min_length=1, max_length=50, description="Name of the world")
    game_day: int = Field(..., ge=0, description="Current game day")
    season: Optional[int] = Field(None, ge=0, description="Current season identifier (optional)")
    size: Optional[int] = Field(None, ge=0, description="Size metric for the world (optional)")
    created_at: Optional[datetime] = Field(None, description="Timestamp when the world was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the world was last updated")

    def __init__(self, **data):
        super().__init__(**data)
        warnings.warn(
            "WorldEntity is deprecated, use app.game_state.entities.world.World for domain logic and "
            "app.api.schemas.world for API validation",
            DeprecationWarning,
            stacklevel=2
        )
    
    class Config:
        from_attributes = True