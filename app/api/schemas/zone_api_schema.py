# app/api/schemas/zone_api_schema.py
from typing import Optional, List
from pydantic import BaseModel, Field, field_serializer
from uuid import UUID
import uuid
from datetime import datetime
from app.game_state.enums.shared import StatusEnum
from app.game_state.enums.zones import ZonalStateEnum

class ZoneBase(BaseModel):
    """Base schema for common zone attributes."""
    id: Optional[UUID] = Field(None, description="Unique identifier for the zone.")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the zone.")
    theme_id: uuid.UUID = Field(..., description="ID of the theme associated with this zone.")
    world_id: uuid.UUID = Field(..., description="ID of the world associated with this zone.")
    description: Optional[str] = Field(None, description="Optional description of the zone.")

class ZoneCreate(ZoneBase):
    """Schema for creating a new zone."""
    status: Optional[StatusEnum] = Field(default=StatusEnum.ACTIVE, description="Status of the zone.")
    biome_id: Optional[UUID] = Field(None, description="ID of the biome associated with this zone.")
    controlling_faction: Optional[UUID] = Field(None, description="ID of the faction controlling this zone.")

class ZoneUpdate(BaseModel):
    """Schema for updating an existing zone."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    theme_id: Optional[UUID] = Field(None,)
    world_id: Optional[UUID] = Field(None,)
    description: Optional[str] = Field(None)
    status: Optional[StatusEnum] = Field(None)
    biome_id: Optional[UUID] = Field(None)
    controlling_faction: Optional[UUID] = Field(None)

class ZoneRead(BaseModel):
    """
    Pydantic Schema for reading/returning a Zone.
    This defines the structure of a Zone object when sent via the API.
    """
    id: UUID  # The primary key, will be populated from the DB model
    name: str
    theme_id: UUID
    world_id: UUID
    description: Optional[str] = None
    status: Optional[str] = None  # Using string to handle enum values
    biome_id: Optional[UUID] = None
    controlling_faction: Optional[UUID] = None
    settlements: Optional[List[UUID]] = Field(default_factory=list)
    biomes: Optional[List[UUID]] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Serializers to handle UUID conversion to string
    @field_serializer('id', 'theme_id', 'world_id', 'biome_id', 'controlling_faction')
    def serialize_uuid(self, uuid_value: Optional[UUID]) -> Optional[str]:
        return str(uuid_value) if uuid_value else None
        
    @field_serializer('settlements', 'biomes')
    def serialize_uuid_list(self, uuid_list: List[UUID]) -> List[str]:
        return [str(u) for u in uuid_list] if uuid_list else []
    
    model_config = {
        "from_attributes": True,  # Allows creating this schema from an ORM object
        "json_schema_extra": {
            "example": {
                "id": "dfba10ac-eaa7-4f83-977d-def25746dfb5",
                "name": "Forest Zone",
                "theme_id": "c4e2d7a9-c12f-1234-5678-c628816ed9de",
                "world_id": "b2494b91-f7d1-4c8d-9da2-c628816ed9de",
                "description": "A dense forest zone with abundant resources",
                "status": "active",
                "state": "peaceful",
                "biome_id": "b5e2d7a9-c12f-1234-5678-c628816ed9de",
                "created_at": "2023-10-27T10:00:00Z",
                "updated_at": "2023-10-28T12:30:00Z"
            }
        }
    }

class ZoneCreatedResponse(BaseModel):
    """Response schema for zone creation endpoint."""
    zone: ZoneBase  # Use ZoneBase for the response
    message: str

class ZonePaginatedResponse(BaseModel):
    """Response schema for paginated zone listing."""
    items: List[ZoneRead]
    total: int
    limit: int
    skip: int
    message: str = "Zones retrieved successfully"

