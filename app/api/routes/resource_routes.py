# --- START - app/api/routes/resource_routes.py ---

from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path
from app.game_state.services.resource_service import ResourceService
from app.game_state.enums.shared import RarityEnum, StatusEnum
from app.game_state.models.resource import ResourceApiModel 
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db
from pydantic import BaseModel, Field 
from typing import List, Optional
from uuid import UUID
import logging

router = APIRouter()

class ResourceCreatePayload(BaseModel):
    """ Pydantic model for the request body when creating a resource type """
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    stack_size: int = Field(100, ge=1)
    rarity: RarityEnum = RarityEnum.COMMON
    status: StatusEnum = StatusEnum.ACTIVE
    theme_id: UUID 

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ancient Oak Wood",
                "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5",
                "description": "Wood from a thousand-year-old tree.",
                "stack_size": 20,
                "rarity": "Rare",
                "status": "Active" 
            }
        }

class ResourceListResponse(BaseModel):
    resources: List[ResourceApiModel]
    total: int

# --- API Routes ---

@router.post(
    "/",
    response_model=ResourceApiModel,
    status_code=201 
)
async def define_new_resource_type(
    payload: ResourceCreatePayload,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Define a new type of Resource in the game system.
    Requires a unique name.
    """
    resource_service = ResourceService(db=db)
    try:
        from uuid import uuid4
        new_resource_id = uuid4()

        created_resource = await resource_service.create_resource_type(
            resource_id=new_resource_id, 
            name=payload.name,
            description=payload.description,
            stack_size=payload.stack_size,
            rarity=payload.rarity,
            status=payload.status,
            theme_id=payload.theme_id
        )
        return created_resource
    except ValueError as ve:
        logging.warning(f"Failed to define resource: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.exception(f"Error defining resource '{payload.name}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error creating resource type.")

@router.get(
    "/{resource_id}",
    response_model=ResourceApiModel,
    summary="Get Resource By ID"
)
async def get_resource_by_id(
    resource_id: UUID = Path(..., description="The unique ID of the resource type"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Retrieve details for a specific resource type using its UUID.
    """
    resource_service = ResourceService(db=db)
    resource = await resource_service.get_resource_by_id(resource_id=resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail=f"Resource type with ID {resource_id} not found.")
    return resource

@router.get(
    "/",
    response_model=ResourceListResponse,
    summary="List Resource Types"
)
async def list_resources(
    rarity: Optional[RarityEnum] = Query(None, description="Filter resources by rarity level"), # Filter by rarity
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"), # Limit results
    db: AsyncSession = Depends(get_async_db)
):
    """
    List available resource types, optionally filtering by rarity.
    Supports basic pagination using skip and limit.
    """
    resource_service = ResourceService(db=db)

    if rarity:
        raise HTTPException(status_code=501, detail="Filtering by rarity not yet implemented.")
    else:
        resources = await resource_service.get_all_resources(skip=skip, limit=limit)

        total = len(resources)
    # -------------------------------------------------------------

    return ResourceListResponse(resources=resources, total=total)

# --- END - app/api/routes/resource_routes.py ---