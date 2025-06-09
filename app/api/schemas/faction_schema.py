# --- FILE: app/api/schemas/faction_schema.py ---

import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class FactionCreate(BaseModel):
    """
    Schema for incoming POST /factions payload.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the faction."
    )
    description: Optional[str] = Field(
        None,
        description="Optional description of the faction."
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Forest",
                "description": "Dense woodland with moderate visibility."
            }
        }
    )


class FactionResponse(BaseModel):
    """
    Schema for outgoing faction data.
    """
    id: uuid.UUID = Field(
        ...,
        description="UUID of the faction."
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the faction."
    )
    description: Optional[str] = Field(
        None,
        description="Optional description of the faction."
    )

    created_at: Optional[datetime] = Field(
        None,
        description="ISO timestamp when the faction was created."
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="ISO timestamp when the faction was last updated."
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "e42a10bc-fab7-4f83-977d-def25746acb7",
                "name": "Forest",
                "description": "Dense woodland with moderate visibility.",
                "created_at": "2025-05-15T10:00:00Z",
                "updated_at": "2025-05-15T10:00:00Z"
            }
        }
    )
