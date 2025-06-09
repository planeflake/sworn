# Example usage and helper functions
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Dict, Any, Optional
from datetime import datetime

class LocationSubtypeCreate(BaseModel):
    """Model for creating new location subtypes (excludes auto-generated fields)"""
    code: str
    name: str
    description: str
    location_type_id: UUID
    theme_id: UUID
    required_attributes: List[Dict[str, Any]] = Field(default_factory=list)
    optional_attributes: List[Dict[str, Any]] = Field(default_factory=list)
    icon_path: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    rarity: Optional[str] = "common"
    generation_weight: float = 1.0

class LocationSubtypeUpdate(BaseModel):
    """Model for updating existing location subtypes (all fields optional)"""
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    location_type_id: Optional[UUID] = None
    theme_id: Optional[UUID] = None
    required_attributes: Optional[List[Dict[str, Any]]] = None
    optional_attributes: Optional[List[Dict[str, Any]]] = None
    icon_path: Optional[str] = None
    tags: Optional[List[str]] = None
    rarity: Optional[str] = None
    generation_weight: Optional[float] = None
    updated_at: datetime = Field(default_factory=datetime.now)

class LocationSubTypeResponse(BaseModel):
    """Model for location subtypes response (excludes auto-generated fields)"""
    id: UUID
    code: str
    name: str
    description: str
    location_type_id: UUID
    theme_id: UUID
    required_attributes: List[Dict[str, Any]] = Field(default_factory=list)
    optional_attributes: List[Dict[str, Any]] = Field(default_factory=list)