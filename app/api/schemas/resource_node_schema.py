# app/api/schemas/resource_node_schema.py

import uuid
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.game_state.enums.shared import StatusEnum
from app.game_state.enums.resource import ResourceNodeVisibilityEnum


class ResourceNodeResourceRead(BaseModel):
    """Resource link in a resource node instance with full details."""
    resource_id: uuid.UUID = Field(..., description="ID of the resource")
    resource_name: Optional[str] = Field(None, description="Name of the resource")
    resource_description: Optional[str] = Field(None, description="Description of the resource")
    resource_rarity: Optional[str] = Field(None, description="Base rarity of the resource")
    resource_stack_size: Optional[int] = Field(None, description="Stack size of the resource")
    
    # Instance-specific extraction data (inherited from blueprint but can be modified)
    is_primary: bool = Field(True, description="Whether this is a primary or secondary resource")
    chance: float = Field(1.0, ge=0.0, le=1.0, description="Current extraction probability")
    amount_min: int = Field(1, ge=1, description="Minimum amount that can be extracted")
    amount_max: int = Field(1, ge=1, description="Maximum amount that can be extracted")
    purity: float = Field(1.0, ge=0.0, le=1.0, description="Current quality/purity")
    rarity: str = Field("common", description="Instance-specific rarity")
    
    # Instance state
    times_extracted: int = Field(0, ge=0, description="Number of times this resource has been extracted")
    total_extracted: int = Field(0, ge=0, description="Total amount of this resource extracted")
    last_extracted_at: Optional[datetime] = Field(None, description="When this resource was last extracted")
    
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
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
                "chance": 0.75,
                "amount_min": 3,
                "amount_max": 7,
                "purity": 0.8,
                "rarity": "common",
                "times_extracted": 15,
                "total_extracted": 87,
                "last_extracted_at": "2023-10-28T14:30:00Z"
            }
        }
    }


class ResourceNodeBase(BaseModel):
    """Base schema for resource node instances."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the resource node")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the node")
    depleted: bool = Field(False, description="Whether the node is currently depleted")
    status: StatusEnum = Field(StatusEnum.PENDING, description="Current status of the node")
    visibility: ResourceNodeVisibilityEnum = Field(ResourceNodeVisibilityEnum.HIDDEN, description="Discovery status")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or len(v.strip()) < 2:
            raise ValueError('Node name must be at least 2 characters')
        return v.strip()


class ResourceNodeCreate(ResourceNodeBase):
    """Schema for creating a new resource node instance."""
    id: Optional[uuid.UUID] = Field(None, description="Optional ID for the node")
    location_id: uuid.UUID = Field(..., description="ID of the location where this node exists")
    blueprint_id: Optional[uuid.UUID] = Field(None, description="Blueprint to create this node from")
    
    # Optional overrides for blueprint resource links
    resource_link_overrides: Optional[Dict[uuid.UUID, Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Per-resource overrides for blueprint settings (resource_id -> override_data)"
    )

    @field_validator('resource_link_overrides')
    @classmethod
    def validate_overrides(cls, v: Optional[Dict[uuid.UUID, Dict[str, Any]]]) -> Dict[uuid.UUID, Dict[str, Any]]:
        if not v:
            return {}
        
        for resource_id, overrides in v.items():
            # Validate chance if provided
            if 'chance' in overrides:
                chance = overrides['chance']
                if not isinstance(chance, (int, float)) or not (0.0 <= chance <= 1.0):
                    raise ValueError(f'Chance must be between 0.0 and 1.0 for resource {resource_id}')
            
            # Validate purity if provided
            if 'purity' in overrides:
                purity = overrides['purity']
                if not isinstance(purity, (int, float)) or not (0.0 <= purity <= 1.0):
                    raise ValueError(f'Purity must be between 0.0 and 1.0 for resource {resource_id}')
            
            # Validate amounts
            if 'amount_min' in overrides and 'amount_max' in overrides:
                if overrides['amount_min'] > overrides['amount_max']:
                    raise ValueError(f'amount_min cannot be greater than amount_max for resource {resource_id}')
        
        return v


class ResourceNodeUpdate(BaseModel):
    """Schema for updating a resource node instance."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    depleted: Optional[bool] = None
    status: Optional[StatusEnum] = None
    visibility: Optional[ResourceNodeVisibilityEnum] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Note: Resource link updates would be handled separately


class ResourceNodeRead(ResourceNodeBase):
    """Schema for reading resource node instances with full details."""
    id: uuid.UUID
    blueprint_id: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Blueprint information
    blueprint_name: Optional[str] = Field(None, description="Name of the source blueprint")
    
    # Location information
    location_name: Optional[str] = Field(None, description="Name of the location")
    location_type: Optional[str] = Field(None, description="Type of the location")
    
    # Full resource extraction information
    resource_links: List[ResourceNodeResourceRead] = Field(
        default_factory=list,
        description="Complete resource extraction information"
    )
    
    # Extraction statistics
    total_resources: int = Field(0, description="Total number of resources this node can yield")
    primary_resources: int = Field(0, description="Number of primary resources")
    secondary_resources: int = Field(0, description="Number of secondary resources")
    total_extractions: int = Field(0, description="Total number of extraction operations performed")
    last_extraction_at: Optional[datetime] = Field(None, description="When any resource was last extracted")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Rich Iron Vein",
                "description": "A rich vein of iron ore discovered in the northern mountains",
                "location_id": "456e7890-e89b-12d3-a456-426614174001",
                "location_name": "Northern Mine",
                "location_type": "settlement",
                "blueprint_id": "789abcde-e89b-12d3-a456-426614174002",
                "blueprint_name": "Iron Vein Blueprint",
                "depleted": False,
                "status": "ACTIVE",
                "visibility": "DISCOVERED",
                "tags": ["mining", "iron", "mountain"],
                "metadata": {
                    "discovered_by": "Miner Joe",
                    "discovery_date": "2023-10-15"
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
                        "chance": 0.8,
                        "amount_min": 5,
                        "amount_max": 10,
                        "purity": 0.85,
                        "rarity": "common",
                        "times_extracted": 23,
                        "total_extracted": 156,
                        "last_extracted_at": "2023-10-28T14:30:00Z"
                    }
                ],
                "total_resources": 2,
                "primary_resources": 1,
                "secondary_resources": 1,
                "total_extractions": 23,
                "last_extraction_at": "2023-10-28T14:30:00Z"
            }
        }
    }


class ResourceNodeSummary(BaseModel):
    """Lightweight summary for listing operations."""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    location_id: uuid.UUID
    location_name: Optional[str] = None
    blueprint_id: Optional[uuid.UUID] = None
    blueprint_name: Optional[str] = None
    depleted: bool
    status: StatusEnum
    visibility: ResourceNodeVisibilityEnum
    total_resources: int = 0
    primary_resources: int = 0
    total_extractions: int = 0
    last_extraction_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }


class ResourceExtractionRequest(BaseModel):
    """Schema for performing resource extraction."""
    extraction_method: Optional[str] = Field("manual", description="Method used for extraction")
    tool_efficiency: float = Field(1.0, ge=0.1, le=2.0, description="Tool efficiency modifier")
    character_skill: float = Field(1.0, ge=0.1, le=2.0, description="Character skill modifier")
    
    @field_validator('tool_efficiency', 'character_skill')
    @classmethod
    def validate_modifiers(cls, v: float) -> float:
        if not (0.1 <= v <= 2.0):
            raise ValueError('Efficiency modifiers must be between 0.1 and 2.0')
        return v


class ResourceExtractionResult(BaseModel):
    """Result of a resource extraction operation."""
    success: bool
    resources_extracted: List[Dict[str, Any]] = Field(default_factory=list)
    node_depleted: bool = False
    message: str = ""
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "resources_extracted": [
                    {
                        "resource_id": "550e8400-e29b-41d4-a716-446655440000",
                        "resource_name": "Iron Ore",
                        "amount": 7,
                        "quality": 0.85
                    }
                ],
                "node_depleted": False,
                "message": "Successfully extracted 7 Iron Ore"
            }
        }
    }