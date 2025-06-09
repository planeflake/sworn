# --- START OF FILE app/api/schemas/theme_schema.py ---

import uuid
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.game_state.enums.theme import Genre

class ThemeBase(BaseModel):
    """Base schema for common theme attributes."""
    name: str = Field(..., min_length=1, max_length=100, description="Unique name of the theme.")
    description: Optional[str] = Field(None, max_length=1000, description="A description of the theme.")

class ThemeCreate(ThemeBase):
    """Schema for creating a new theme. Can optionally accept an ID for seeding."""
    id: Optional[uuid.UUID] = Field(None, description="Optional ID for the theme, usually for seeding. Will be generated if not provided.")
    # Add any other fields specific to creation if needed

class ThemeUpdate(BaseModel):
    """Schema for updating a theme. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    # Add any other updatable fields

class ThemeRead(ThemeBase):
    """
    Pydantic Schema for reading/returning a Theme.
    This defines the structure of a Theme object when sent via the API.
    """
    id: uuid.UUID # The primary key, will be populated from the DB model
    fullname: str
    genre: Optional[Genre] = None

    created_at: datetime
    updated_at: datetime # Assuming updated_at is non-nullable in your DB model

    model_config = ConfigDict( # Pydantic v2+
        from_attributes=True, # Allows creating this schema from an ORM object or dataclass
        json_schema_extra={
            "example": {
                "id": "dfba10ac-eaa7-4f83-977d-def25746dfb5",
                "name": "Fantasy Basic",
                "fullname": "Fantasy Basic (Fantasy)",
                "description": "A generic fantasy theme with magic and medieval elements.",
                "created_at": "2023-10-27T10:00:00Z",
                "updated_at": "2023-10-28T12:30:00Z"
            }
        }
    )

# --- END OF FILE app/api/schemas/theme_schema.py ---