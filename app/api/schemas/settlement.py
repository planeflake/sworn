# app/api/schemas/settlement.py
import uuid
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime

class SettlementBase(BaseModel):
    """Base schema for common settlement attributes."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the settlement.")
    description: Optional[str] = Field(None, max_length=1000, description="A description of the settlement.")
    world_id: uuid.UUID = Field(..., description="ID of the world this settlement belongs to.")
    population: int = Field(0, ge=0, description="Current population of the settlement.")
    buildings: List[str] = Field(default_factory=list, description="List of building types for this settlement.")

class SettlementCreate(SettlementBase):
    """Schema for creating a new settlement."""
    leader_id: Optional[uuid.UUID] = Field(None, description="ID of the character who is the leader of this settlement.")
    # Add any other fields specific to creation if needed

class SettlementUpdate(BaseModel):
    """Schema for updating a settlement. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    leader_id: Optional[uuid.UUID] = None
    # Add any other updatable fields

class ResourceQuantity(BaseModel):
    """Schema for a resource and its quantity."""
    resource_id: uuid.UUID = Field(..., description="ID of the resource")
    quantity: int = Field(..., ge=1, description="Quantity of the resource")

class SettlementRead(SettlementBase):
    """
    Pydantic Schema for reading/returning a Settlement.
    This defines the structure of a Settlement object when sent via the API.
    """
    id: uuid.UUID
    leader_id: Optional[uuid.UUID] = None
    population: int = 0
    buildings: List[Any] = []
    resources: Dict[str, int] = Field(default_factory=dict, description="Dictionary mapping resource UUIDs to quantities")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "dfba10ac-eaa7-4f83-977d-def25746dfb5",
                "name": "Riverside Village",
                "description": "A small settlement by the river.",
                "world_id": "5d937fc9-b4c7-4cc7-b6af-318c2fa6c73c",
                "leader_id": "7b32cfd4-8291-4d3e-b8a9-c9bce3d9d15b",
                "population": 50,
                "buildings": ["town_hall", "farm", "blacksmith"],
                "resources": {
                    "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d": 100,  # UUID of wheat, 100 units
                    "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e": 50,   # UUID of iron, 50 units
                    "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f": 200   # UUID of wood, 200 units
                },
                "created_at": "2023-10-27T10:00:00Z",
                "updated_at": "2023-10-28T12:30:00Z"
            }
        }
    }