# app/api/schemas/resource_node_blueprint_schema.py

import uuid
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.game_state.enums.shared import StatusEnum


class ResourceLinkBase(BaseModel):
    """Base schema for resource links in blueprints."""
    resource_id: uuid.UUID = Field(..., description="ID of the resource that can be extracted")
    is_primary: bool = Field(True, description="Whether this is a primary or secondary resource")
    chance: float = Field(1.0, ge=0.0, le=1.0, description="Probability of extracting this resource (0.0-1.0)")
    amount_min: int = Field(1, ge=1, description="Minimum amount that can be extracted")
    amount_max: int = Field(1, ge=1, description="Maximum amount that can be extracted")
    purity: float = Field(1.0, ge=0.0, le=1.0, description="Quality/purity of the extracted resource")
    rarity: str = Field("common", description="Rarity classification of this resource in this node")
    theme_id: Optional[uuid.UUID] = Field(None, description="Theme associated with this resource link")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class ResourceLinkCreate(ResourceLinkBase):
    """Schema for creating resource links in blueprints."""
    pass


class ResourceLinkUpdate(BaseModel):
    """Schema for updating resource links."""
    is_primary: Optional[bool] = None
    chance: Optional[float] = Field(None, ge=0.0, le=1.0)
    amount_min: Optional[int] = Field(None, ge=1)
    amount_max: Optional[int] = Field(None, ge=1)
    purity: Optional[float] = Field(None, ge=0.0, le=1.0)
    rarity: Optional[str] = None
    theme_id: Optional[uuid.UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class ResourceLinkRead(ResourceLinkBase):
    """Schema for reading resource links with full resource details."""
    # Full resource details to reduce API calls
    resource_name: Optional[str] = Field(None, description="Name of the resource")
    resource_description: Optional[str] = Field(None, description="Description of the resource")
    resource_rarity: Optional[str] = Field(None, description="Base rarity of the resource")
    resource_stack_size: Optional[int] = Field(None, description="Stack size of the resource")
    
    # Theme details if present
    theme_name: Optional[str] = Field(None, description="Name of the associated theme")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "resource_id": "550e8400-e29b-41d4-a716-446655440000",
                "resource_name": "Iron Ore",
                "resource_description": "Raw iron ore that can be smelted",
                "resource_rarity": "common",
                "resource_stack_size": 50,
                "is_primary": True,
                "chance": 0.8,
                "amount_min": 3,
                "amount_max": 7,
                "purity": 0.9,
                "rarity": "common",
                "theme_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "theme_name": "Medieval Mining"
            }
        }
    }


class ResourceNodeBlueprintBase(BaseModel):
    """Base schema for resource node blueprints."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the blueprint")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the blueprint")
    biome_type: Optional[str] = Field(None, max_length=50, description="Associated biome type")
    depleted: bool = Field(False, description="Whether nodes from this blueprint start depleted")
    status: StatusEnum = Field(StatusEnum.PENDING, description="Status of the blueprint")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class ResourceNodeBlueprintCreate(ResourceNodeBlueprintBase):
    """Schema for creating a new resource node blueprint."""
    id: Optional[uuid.UUID] = Field(None, description="Optional ID for the blueprint")
    resource_links: Optional[List[ResourceLinkCreate]] = Field(
        default_factory=list, 
        description="Resources that can be extracted from nodes using this blueprint"
    )


class ResourceNodeBlueprintUpdate(BaseModel):
    """Schema for updating a resource node blueprint."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    biome_type: Optional[str] = Field(None, max_length=50)
    depleted: Optional[bool] = None
    status: Optional[StatusEnum] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    # Note: resource_links updates would be handled separately for complexity


class ResourceNodeBlueprintRead(ResourceNodeBlueprintBase):
    """Schema for reading resource node blueprints with full details."""
    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Full resource links with detailed information
    resource_links: List[ResourceLinkRead] = Field(
        default_factory=list,
        description="Complete resource extraction information"
    )
    
    # Summary statistics for quick reference
    total_resources: int = Field(0, description="Total number of resources this blueprint can yield")
    primary_resources: int = Field(0, description="Number of primary resources")
    secondary_resources: int = Field(0, description="Number of secondary resources")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Iron Vein Blueprint",
                "description": "A blueprint for creating iron ore veins in mountainous regions",
                "biome_type": "mountain",
                "depleted": False,
                "status": "ACTIVE",
                "tags": ["mining", "iron", "mountain"],
                "metadata": {
                    "difficulty": "easy",
                    "required_tools": ["pickaxe"]
                },
                "created_at": "2023-10-27T10:00:00Z",
                "updated_at": "2023-10-28T12:30:00Z",
                "resource_links": [
                    {
                        "resource_id": "550e8400-e29b-41d4-a716-446655440000",
                        "resource_name": "Iron Ore",
                        "resource_description": "Raw iron ore that can be smelted",
                        "resource_rarity": "common",
                        "resource_stack_size": 50,
                        "is_primary": True,
                        "chance": 0.9,
                        "amount_min": 5,
                        "amount_max": 10,
                        "purity": 0.8,
                        "rarity": "common"
                    },
                    {
                        "resource_id": "550e8400-e29b-41d4-a716-446655440001",
                        "resource_name": "Stone",
                        "resource_description": "Common building stone",
                        "resource_rarity": "common",
                        "resource_stack_size": 100,
                        "is_primary": False,
                        "chance": 0.3,
                        "amount_min": 1,
                        "amount_max": 3,
                        "purity": 1.0,
                        "rarity": "common"
                    }
                ],
                "total_resources": 2,
                "primary_resources": 1,
                "secondary_resources": 1
            }
        }
    }


class ResourceNodeBlueprintSummary(BaseModel):
    """Lightweight summary for listing operations."""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    biome_type: Optional[str] = None
    status: StatusEnum
    total_resources: int = 0
    primary_resources: int = 0
    created_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }