"""
API schemas for location types.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class AttributeDefinition(BaseModel):
    """Schema for attribute definition."""
    name: str
    type: str  # 'string', 'number', 'integer', 'boolean', 'array', 'object'
    description: Optional[str] = None
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None  # Possible values for this attribute
    
    model_config = ConfigDict(from_attributes=True)

class LocationTypeBase(BaseModel):
    """Base schema for location type data."""
    code: str
    name: str
    description: Optional[str] = None
    theme: Optional[str] = None
    can_contain: List[str] = Field(default_factory=list)
    required_attributes: List[AttributeDefinition] = Field(default_factory=list)
    optional_attributes: List[AttributeDefinition] = Field(default_factory=list)
    icon_path: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class LocationTypeCreate(LocationTypeBase):
    """Schema for creating a new location type."""
    pass

class LocationTypeUpdate(BaseModel):
    """Schema for updating a location type."""
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    theme: Optional[str] = None
    can_contain: Optional[List[str]] = None
    required_attributes: Optional[List[AttributeDefinition]] = None
    optional_attributes: Optional[List[AttributeDefinition]] = None
    icon_path: Optional[str] = None
    tags: Optional[List[str]] = None

class LocationTypeResponse(LocationTypeBase):
    """Schema for location type response."""
    id: UUID
    created_at: str
    updated_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)