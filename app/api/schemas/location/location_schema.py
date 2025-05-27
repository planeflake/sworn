"""
API schemas for locations.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict

class LocationBase(BaseModel):
    """Base schema for location data."""
    name: str
    description: Optional[str] = None
    # Allow providing either ID or code for type references
    location_type_id: Optional[UUID] = None  
    location_type_code: Optional[str] = None
    # Parent reference (optional)
    parent_id: Optional[UUID] = None
    parent_type_id: Optional[UUID] = None
    parent_type_code: Optional[str] = None
    # Other attributes
    coordinates: Optional[Dict[str, float]] = None
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)
    is_active: Optional[bool] = True

class LocationCreate(LocationBase):
    """Schema for creating a new location."""
    # Make sure we have either location_type_id or location_type_code
    @model_validator(mode='after')
    def validate_location_type(self):
        if not self.location_type_id and not self.location_type_code:
            raise ValueError("Either location_type_id or location_type_code must be provided")
        
        # For parent references, ensure we have type information if parent_id is present
        if self.parent_id and not (self.parent_type_id or self.parent_type_code):
            raise ValueError("If parent_id is provided, either parent_type_id or parent_type_code must also be provided")
            
        return self

class LocationUpdate(BaseModel):
    """Schema for updating a location."""
    name: Optional[str] = None
    description: Optional[str] = None
    location_type_id: Optional[UUID] = None
    location_type_code: Optional[str] = None
    parent_id: Optional[UUID] = None
    parent_type_id: Optional[UUID] = None
    parent_type_code: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    attributes: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

class LocationReference(BaseModel):
    """Schema for location reference."""
    id: UUID
    name: str
    location_type_id: UUID
    location_type_code: str
    
    model_config = ConfigDict(from_attributes=True)

class LocationSubTypeResponse(BaseModel):
    """Schema for location sub-type reference."""
    id: UUID
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class ThemeReference(BaseModel):
    """Schema for theme reference."""
    id: UUID
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class BiomeReference(BaseModel):
    """Schema for biome reference."""
    id: UUID
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class FactionReference(BaseModel):
    """Schema for faction reference."""
    id: UUID
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class BuildingUpgradeResponse(BaseModel):
    """Schema for building upgrade option."""
    id: UUID
    name: str
    resources: List[Dict[str, Any]]
    bonus: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)

class BuildingResponse(BaseModel):
    """Schema for building in location."""
    building_id: UUID
    name: str
    building_type: str
    level: int
    status: str
    upgrades: List[BuildingUpgradeResponse] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)

class ResourceResponse(BaseModel):
    """Schema for resource in location."""
    resource_id: UUID
    name: str
    quantity: int
    unit: str
    
    model_config = ConfigDict(from_attributes=True)

class ResourceNodeResponse(BaseModel):
    """Schema for resource node in location."""
    node_id: UUID
    resource_id: UUID
    name: str
    extraction_rate: int
    max_extraction_rate: int
    unit: str
    depleted: bool
    
    model_config = ConfigDict(from_attributes=True)

class TravelConnectionResponse(BaseModel):
    """Schema for travel connection."""
    travel_link_id: UUID
    name: str
    biomes: List[BiomeReference] = Field(default_factory=list)
    factions: List[FactionReference] = Field(default_factory=list)
    speed: float
    path_type: str
    terrain_modifier: float
    danger_level: int
    visibility: str
    
    model_config = ConfigDict(from_attributes=True)

class LocationResponse(BaseModel):
    """Schema for location response."""
    id: UUID
    name: str
    description: Optional[str] = None
    location_type_id: UUID
    location_sub_type: Optional[LocationSubTypeResponse] = None
    theme_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None
    biome_id: Optional[UUID] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    coordinates: Dict[str, float] = Field(default_factory=dict)
    is_active: bool = True
    created_at: str
    updated_at: Optional[str] = None
    buildings: List[BuildingResponse] = Field(default_factory=list)
    resources: List[ResourceResponse] = Field(default_factory=list)
    resource_nodes: List[ResourceNodeResponse] = Field(default_factory=list)
    travel_connections: List[TravelConnectionResponse] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)