"""
API routes for locations.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db
from app.api.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationResponse
)
from app.game_state.services.location.location_service import LocationService
from app.game_state.services.location.location_type_service import LocationTypeService
from app.api.routes.location.location_route_utils import build_location_response

router = APIRouter()

@router.get("/", response_model=List[LocationResponse])
async def get_locations(
    type_id: Optional[UUID] = Query(None, description="Filter by location type ID"),
    type_code: Optional[str] = Query(None, description="Filter by location type code"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get locations with optional filters."""
    location_service = LocationService(db)
    type_service = LocationTypeService(db)

    if parent_id:
        child_type_id = type_id
        if not child_type_id and type_code:
            type_entity = await type_service.get_type_by_code(type_code)
            child_type_id = type_entity.entity_id if type_entity else None

        locations = await location_service.get_children(parent_id, child_type_id)
    elif type_id:
        locations = await location_service.get_locations_by_type_id(type_id, limit, offset)
    elif type_code:
        locations = await location_service.get_locations_by_type_code(type_code, limit, offset)
    else:
        world_type = await type_service.get_type_by_code("world")
        locations = await location_service.get_locations_by_type_id(world_type.entity_id, limit, offset) if world_type else []

    return [await build_location_response(loc, location_service) for loc in locations]


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a location by ID."""
    location_service = LocationService(db)
    location = await location_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return await build_location_response(location, location_service)


@router.post("/", response_model=LocationResponse)
async def create_location(
    location_data: LocationCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new location."""
    location_service = LocationService(db)
    try:
        location = await location_service.create_location(location_data.model_dump(exclude_unset=True))
        return await build_location_response(location, location_service)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: UUID, 
    location_data: LocationUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update an existing location."""
    location_service = LocationService(db)
    try:
        location = await location_service.update_location(
            location_id,
            location_data.model_dump(exclude_unset=True)
        )
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        return await build_location_response(location, location_service)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))