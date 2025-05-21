# --- START OF FILE app/api/schemas/biome_schema.py ---

import uuid
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, Dict
from datetime import datetime

class BiomeCreate(BaseModel):
    """Schema for creating a new biome. Can optionally accept an ID for seeding."""
    id: Optional[uuid.UUID] = Field(None,
                               description="Optional UUID for the biome, will be generated if not provided.")
    biome_id: str = Field(..., description="String identifier for the biome (e.g., 'forest', 'plains').")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the biome.")
    display_name: Optional[str] = Field(None, description="User-friendly display name of the biome (defaults to name if not provided).")
    description: Optional[str] = Field(None, description="Optional description of the biome.")
    base_movement_modifier: Optional[float] = Field(1.0, description="Movement speed multiplier (1.0 = normal).")
    danger_level_base: Optional[int] = Field(1, ge=1, le=5, description="Base danger level (1-5).")
    resource_types: Optional[Dict[str, float]] = Field(default={}, description="Dictionary of resource types and their abundance multipliers.")
    color_hex: Optional[str] = Field(None, description="Hexadecimal color code for map display.")
    icon_path: Optional[str] = Field(None, description="Path to biome icon image.")

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

class BiomeRead(BaseModel):
    """
    Pydantic Schema for reading/returning a Biome.
    This defines the structure of a Biome object when sent via the API.
    """
    id: uuid.UUID  # The primary key, will be populated from the DB model
    biome_id: str  # String identifier like 'forest', 'plains', etc.
    name: str
    display_name: str
    description: Optional[str] = None
    base_movement_modifier: float
    danger_level_base: int
    resource_types: Optional[Dict[str, float]] = None
    color_hex: Optional[str] = None
    icon_path: Optional[str] = None
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