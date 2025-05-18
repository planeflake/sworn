# app/api/schemas/world.py
import uuid
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class WorldBase(BaseModel):
    """Base schema for common world attributes."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the world.")
    theme_id: uuid.UUID = Field(..., description="ID of the theme associated with this world.")
    id: Optional[UUID] = Field(None, description="Unique identifier for the world.")

class WorldCreate(WorldBase):
    """Schema for creating a new world."""
    description: Optional[str] = Field(None, max_length=1000, description="A description of the world.")
    # Add any other fields specific to creation if needed

class WorldUpdate(BaseModel):
    """Schema for updating a world. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    theme_id: Optional[uuid.UUID] = None
    day: Optional[int] = Field(None, ge=0, description="Current game day in the world.")
    # Add any other updatable fields

class WorldRead(WorldBase):
    """
    Pydantic Schema for reading/returning a World.
    This defines the structure of a World object when sent via the API.
    """
    id: uuid.UUID
    description: Optional[str] = None
    game_day: int = Field(0, description="Current game day in the world.")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Optional additional data (can be extended based on your needs)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata about the world.")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "dfba10ac-eaa7-4f83-977d-def25746dfb5",
                "name": "Eldoria",
                "description": "A magical realm of ancient forests and mystical creatures.",
                "theme_id": "5d937fc9-b4c7-4cc7-b6af-318c2fa6c73c",
                "day": 42,
                "created_at": "2023-10-27T10:00:00Z",
                "updated_at": "2023-10-28T12:30:00Z",
                "metadata": {
                    "active_seasons": ["spring", "summer"],
                    "weather_patterns": ["rainy", "sunny", "foggy"]
                }
            }
        }
    }

class WorldCreateRequest(BaseModel):
    name: str = Field(None, description="Desired name for the world (optional, random if None)", max_length=50)
    size: int = Field(1000, description="Size indicator for the world (optional)", ge=0)
    theme_id: UUID = Field(..., description="The required ID of the theme to assign to the new world")
    description: Optional[str] = Field(None, description="Description of the world (optional)", max_length=1000)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "random_world",
                    "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5"
                }
            ]
        }
    }
