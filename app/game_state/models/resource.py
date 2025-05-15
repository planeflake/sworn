"""
DEPRECATED: This model is being phased out in favor of using app.game_state.entities.resource.ResourceEntity directly.
Use app.game_state.entities.resource.ResourceEntity for domain logic and app.api.schemas.resource for API validation.
"""
import warnings
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from app.game_state.enums.shared import RarityEnum, StatusEnum

warnings.warn(
    "ResourceApiModel is deprecated, use app.game_state.entities.resource.ResourceEntity for domain logic and "
    "app.api.schemas.resource for API validation",
    DeprecationWarning,
    stacklevel=2
)

class ResourceApiModel(BaseModel):
    """
    DEPRECATED: Use app.game_state.entities.resource.ResourceEntity and app.api.schemas.resource instead.
    This class is maintained for backward compatibility during transition.
    """
    # --- Identifier ---
    resource_id: uuid.UUID = Field(...)

    # --- Basic Resource Information ---
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    rarity: RarityEnum = RarityEnum.COMMON
    stack_size: int = Field(..., ge=1)
    status: StatusEnum = StatusEnum.ACTIVE
    theme_id: uuid.UUID = None

    # --- Timestamps ---
    created_at: Optional[datetime] = Field(None)
    updated_at: Optional[datetime] = Field(None)

    def __init__(self, **data):
        super().__init__(**data)
        warnings.warn(
            "ResourceApiModel is deprecated, use app.game_state.entities.resource.ResourceEntity for domain logic and "
            "app.api.schemas.resource for API validation",
            DeprecationWarning,
            stacklevel=2
        )

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "resource_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "name": "Iron Ore",
                "description": "A chunk of raw iron.",
                "rarity": "Uncommon",
                "stack_size": 50,
                "status": "ACTIVE",
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-10T15:30:00Z",
            }
        }