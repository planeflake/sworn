"""
API schemas for locations with automatic validation support.
"""
from typing import Optional, List, Dict, Any, Annotated
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict

# Import for compatibility rules
from app.game_state.services.core.validation.service_validaton_utils import CompatibilityRule

# ==============================================================================
# GENERIC REFERENCE MODEL
# ==============================================================================

class Reference(BaseModel):
    """Generic reference schema for any entity with id and name."""
    id: UUID
    name: str
    code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# LOCATION SCHEMAS
# ==============================================================================

class LocationBase(BaseModel):
    """Base schema for location data."""
    name: str
    description: Optional[str] = None

    # Location type reference (allow either ID or code)
    location_type_id: Optional[UUID] = None
    location_type_code: Optional[str] = None

    # Location subtype with automatic compatibility validation
    location_sub_type_id: Annotated[Optional[UUID], CompatibilityRule(
        parent_field="location_type_id"
    )] = None

    # Polymorphic parent reference
    parent_id: Optional[UUID] = None
    parent_type: Optional[str] = None  # "location", "region", "area", etc.

    # Standard foreign keys (auto-validated)
    theme_id: Optional[UUID] = None
    world_id: Optional[UUID] = None
    biome_id: Optional[UUID] = None

    # Other attributes
    coordinates: Optional[Dict[str, float]] = None
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tags: Optional[List[str]] = Field(default_factory=list)
    is_active: Optional[bool] = True


class LocationCreate(LocationBase):
    """Schema for creating a new location."""

    @model_validator(mode='after')
    def validate_required_fields(self):
        if not self.location_type_id and not self.location_type_code:
            raise ValueError("Either location_type_id or location_type_code must be provided")

        if self.parent_id and not self.parent_type:
            raise ValueError("If parent_id is provided, parent_type must also be provided")

        return self


class LocationUpdate(BaseModel):
    """Schema for updating a location."""
    name: Optional[str] = None
    description: Optional[str] = None
    location_type_id: Optional[UUID] = None
    location_type_code: Optional[str] = None
    location_sub_type_id: Annotated[Optional[UUID], CompatibilityRule(
        parent_field="location_type_id"
    )] = None
    parent_id: Optional[UUID] = None
    parent_type: Optional[str] = None
    theme_id: Optional[UUID] = None
    world_id: Optional[UUID] = None
    biome_id: Optional[UUID] = None
    coordinates: Optional[Dict[str, float]] = None
    attributes: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


# ==============================================================================
# RELATED ENTITY SCHEMAS
# ==============================================================================

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
    biomes: List[Reference] = Field(default_factory=list)
    factions: List[Reference] = Field(default_factory=list)
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

    # All references use the generic Reference model
    location_type: Reference
    location_sub_type: Optional[Reference] = None
    theme: Optional[Reference] = None
    world: Optional[Reference] = None
    biome: Optional[Reference] = None
    type_id: Optional[UUID] = None
    type_code: Optional[str] = None
    type: Optional[str] = None
    # Polymorphic parent reference
    parent_id: Optional[UUID] = None
    parent_type: Optional[str] = None
    parent: Optional[Reference] = None

    # Other data
    attributes: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    coordinates: Dict[str, float] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[str] = None

    # Related data
    buildings: List[BuildingResponse] = Field(default_factory=list)
    resources: List[ResourceResponse] = Field(default_factory=list)
    resource_nodes: List[ResourceNodeResponse] = Field(default_factory=list)
    travel_connections: List[TravelConnectionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)