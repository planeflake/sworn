# --- START OF FILE app/game_state/models/resource.py ---

import uuid
from datetime import datetime
from typing import Optional # Removed List, Dict, Any as not used

# --- Pydantic Imports ---
from pydantic import BaseModel, Field

# --- Import API Enums ---
from app.game_state.enums.shared import RarityEnum, StatusEnum # Keep both

# --- API Model Definition ---
class ResourceApiModel(BaseModel):
    """
    API MODEL (DTO) for Resource Types.
    Defines the data structure for API requests/responses related to resources.
    """
    # --- Identifier ---
    resource_id: uuid.UUID = Field(...)

    # --- Basic Resource Information ---
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    rarity: RarityEnum = RarityEnum.COMMON # Required in API response (has default)
    stack_size: int = Field(..., ge=1) # Required in API response (add default if desired: default=100)
    status: StatusEnum = StatusEnum.ACTIVE # Required in API response (has default)
    theme_id: uuid.UUID = None # Optional, can be None

    # --- Timestamps ---
    created_at: Optional[datetime] = Field(None)
    updated_at: Optional[datetime] = Field(None)

    # --- Pydantic Configuration ---
    class Config:
        from_attributes = True # Allows Pydantic to populate from ORM attributes

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

# --- END OF FILE app/game_state/models/resource.py ---