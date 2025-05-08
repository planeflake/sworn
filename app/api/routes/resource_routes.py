# --- START - app/api/routes/resource_routes.py ---

import logging
from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path # Import necessary components
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field # Import Pydantic for data validation and serialization

# Import DB dependency, Service, API Model, and Enums
from app.db.dependencies import get_async_db
from app.game_state.services.resource_service import ResourceService
from app.game_state.models.resource import ResourceApiModel # Used for responses and potentially requests
from app.game_state.enums.shared import RarityEnum, StatusEnum

# Define Router
router = APIRouter()

# --- Define Request Models (if needed for complex inputs) ---
# For creating a resource, we often take individual fields
class ResourceCreatePayload(BaseModel):
    """ Pydantic model for the request body when creating a resource type """
    # ID is often assigned by the system or passed separately
    # resource_id: UUID # If client needs to suggest an ID (less common for types)
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    stack_size: int = Field(100, ge=1)
    rarity: RarityEnum = RarityEnum.COMMON
    status: StatusEnum = StatusEnum.ACTIVE
    theme_id: UUID # Optional theme ID

    class Config:
        # Example for API documentation if using this model directly
        json_schema_extra = {
            "example": {
                "name": "Ancient Oak Wood",
                "theme_id": "dfba10ac-eaa7-4f83-977d-def25746dfb5",
                "description": "Wood from a thousand-year-old tree.",
                "stack_size": 20,
                "rarity": "Rare", # Use Enum value name
                "status": "Active" # Use Enum value name
            }
        }


# --- Define Response Models ---
# Re-use ResourceApiModel for single resource responses
# Create a model for list responses
class ResourceListResponse(BaseModel):
    resources: List[ResourceApiModel]
    total: int # Optional: include total count if implementing pagination fully

# --- API Routes ---

@router.post(
    "/",
    response_model=ResourceApiModel, # Return the created resource
    status_code=201 # HTTP status code for successful creation
)
async def define_new_resource_type(
    # Use the Pydantic model to parse the request body
    payload: ResourceCreatePayload,
    # You might want to generate the UUID server-side instead of client-side
    # resource_id: UUID = Body(default_factory=uuid.uuid4), # Example server-side generation
    db: AsyncSession = Depends(get_async_db)
):
    """
    Define a new type of Resource in the game system.
    Requires a unique name.
    """
    resource_service = ResourceService(db=db)
    try:
        # Generate ID here if not provided by client
        from uuid import uuid4
        new_resource_id = uuid4()

        created_resource = await resource_service.create_resource_type(
            # Pass data from the validated payload
            resource_id=new_resource_id, # Use generated or client-provided ID
            name=payload.name,
            description=payload.description,
            stack_size=payload.stack_size,
            rarity=payload.rarity,
            status=payload.status,
            theme_id=payload.theme_id # Assuming this is a UUID
        )
        return created_resource
    except ValueError as ve: # Catch validation errors from service/manager
        logging.warning(f"Failed to define resource: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e: # Catch unexpected errors (like DB unique constraint)
        logging.exception(f"Error defining resource '{payload.name}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error creating resource type.")


@router.get(
    "/{resource_id}",
    response_model=ResourceApiModel,
    summary="Get Resource By ID"
)
async def get_resource_by_id(
    resource_id: UUID = Path(..., description="The unique ID of the resource type"), # Get ID from path
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
    response_model=ResourceListResponse, # Use the list response model
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

    # --- Add filtering logic in the Service/Repository later ---
    # For now, just demonstrating the query parameter
    if rarity:
        # Placeholder: You would need to implement find_by_rarity in the service/repo
        # resources = await resource_service.find_by_rarity(rarity=rarity, skip=skip, limit=limit)
        # total = await resource_service.count_by_rarity(rarity=rarity) # Need a count method too
        # For now, raise error if filter is used but not implemented:
        raise HTTPException(status_code=501, detail="Filtering by rarity not yet implemented.")
    else:
        # Fetch all using existing service method
        resources = await resource_service.get_all_resources(skip=skip, limit=limit)
        # Placeholder for total count - requires another query in repo/service
        # total = await resource_service.count_all_resources()
        total = len(resources) # Temporary approximation for total
    # -------------------------------------------------------------

    return ResourceListResponse(resources=resources, total=total)


# --- Placeholder for "Resources by Character ID" ---
# This endpoint doesn't belong here as this file manages RESOURCE TYPES.
# Listing resources owned by a character would typically be:
# - GET /characters/{character_id}/inventory  (on character_routes.py)
# - GET /inventory?character_id={character_id} (on inventory_routes.py)
# It would involve fetching character inventory data, likely linking item instances
# back to these resource type definitions.

# @router.get("/by-character/{character_id}", ...)
# async def list_resources_for_character(...):
#    # Needs Character/Inventory Service & Repository logic
#    raise HTTPException(status_code=501, detail="Listing resources by character not implemented here.")

# --- END - app/api/routes/resource_routes.py ---