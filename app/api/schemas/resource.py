# app/api/schemas/resource.py
import uuid
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from app.game_state.enums.shared import RarityEnum, StatusEnum

class ResourceBase(BaseModel):
    """Base schema for common resource attributes."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the resource.")
    description: Optional[str] = Field(None, max_length=1000, description="A description of the resource.")
    stack_size: int = Field(default=100, ge=1, description="Maximum stack size for this resource.")
    rarity: RarityEnum = Field(default=RarityEnum.COMMON, description="Rarity level of the resource.")
    status: StatusEnum = Field(default=StatusEnum.ACTIVE, description="Current status of the resource.")

class ResourceCreate(ResourceBase):
    """Schema for creating a new resource."""
    id: Optional[uuid.UUID] = Field(None, description="Optional ID for the resource. Will be generated if not provided.")
    theme_id: Optional[uuid.UUID] = Field(None, description="Optional ID of the theme associated with this resource.")
    # Add any other fields specific to creation if needed

class ResourceUpdate(BaseModel):
    """Schema for updating a resource. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    stack_size: Optional[int] = Field(None, ge=1)
    rarity: Optional[RarityEnum] = None
    status: Optional[StatusEnum] = None
    theme_id: Optional[uuid.UUID] = None
    # Add any other updatable fields

class ResourceRead(ResourceBase):
    """
    Pydantic Schema for reading/returning a Resource.
    This defines the structure of a Resource object when sent via the API.
    """
    resource_id: uuid.UUID
    theme_id: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Optional metadata (if your resource has additional properties)
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional resource attributes.")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "resource_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5",
                "name": "Iron Ore",
                "description": "Raw iron ore extracted from mines.",
                "stack_size": 50,
                "rarity": "Common",
                "status": "Active",
                "theme_id": "5d937fc9-b4c7-4cc7-b6af-318c2fa6c73c",
                "created_at": "2023-10-27T10:00:00Z",
                "updated_at": "2023-10-28T12:30:00Z",
                "attributes": {
                    "weight": 2.5,
                    "value": 5,
                    "source": ["mining", "trading"]
                }
            }
        }
    }