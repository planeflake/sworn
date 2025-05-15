# --- START OF FILE app/api/schemas/biome_schema.py ---

import uuid
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, Dict
from datetime import datetime

class BiomeBase(BaseModel):
    """Base schema for common biome attributes."""
    biome_id: str = Field(..., min_length=1, max_length=50, 
                      description="Unique string identifier for the biome.")
    name: str = Field(..., min_length=1, max_length=100, 
                 description="Name of the biome.")
    display_name: str = Field(..., min_length=1, max_length=100, 
                        description="User-friendly display name for the biome.")
    description: Optional[str] = Field(None, max_length=1000, 
                                 description="Detailed description of the biome.")
    
    # Gameplay attributes
    base_movement_modifier: float = Field(1.0, ge=0.1, le=2.0, 
                                    description="Movement speed multiplier (1.0 = normal)")
    danger_level_base: int = Field(1, ge=1, le=5, 
                             description="Base danger level (1-5)")
    resource_types: Dict[str, float] = Field(default_factory=dict, 
                                      description="Dictionary of resource types and their abundance multipliers")
    
    # Visual representation
    color_hex: Optional[str] = Field(None, min_length=4, max_length=9, 
                               description="Hexadecimal color code (e.g., #90EE90)")
    icon_path: Optional[str] = Field(None, max_length=255, 
                               description="Path to biome icon image")

class BiomeCreate(BiomeBase):
    """Schema for creating a new biome. Can optionally accept an ID for seeding."""
    id: Optional[uuid.UUID] = Field(None, 
                               description="Optional ID for the biome, usually for seeding. Will be generated if not provided.")
    # Add any other fields specific to creation if needed

class BiomeUpdate(BaseModel):
    """Schema for updating a biome. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    base_movement_modifier: Optional[float] = Field(None, ge=0.1, le=2.0)
    danger_level_base: Optional[int] = Field(None, ge=1, le=5)
    resource_types: Optional[Dict[str, float]] = Field(None)
    color_hex: Optional[str] = Field(None, min_length=4, max_length=9)
    icon_path: Optional[str] = Field(None, max_length=255)

class BiomeRead(BiomeBase):
    """
    Pydantic Schema for reading/returning a Biome.
    This defines the structure of a Biome object when sent via the API.
    """
    id: uuid.UUID  # The primary key, will be populated from the DB model
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Serializer to handle UUID conversion to string if needed
    @field_serializer('id')
    def serialize_id(self, id: uuid.UUID):
        return str(id)

    model_config = {  # Pydantic v2+
        "from_attributes": True,  # Allows creating this schema from an ORM object or dataclass
        "json_schema_extra": {
            "example": {
                "id": "e42a10bc-fab7-4f83-977d-def25746acb7",
                "biome_id": "forest",
                "name": "Forest",
                "display_name": "Forest",
                "description": "Dense woodland with moderate visibility.",
                "base_movement_modifier": 0.8,
                "danger_level_base": 2,
                "resource_types": {"food": 1.0, "wood": 1.5, "herbs": 1.3},
                "color_hex": "#228B22",
                "icon_path": None,
                "created_at": "2025-05-15T10:00:00Z",
                "updated_at": "2025-05-15T10:00:00Z"
            }
        }
    }

# --- END OF FILE app/api/schemas/biome_schema.py ---