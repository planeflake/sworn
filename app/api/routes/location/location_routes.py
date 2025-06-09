"""
API routes for locations.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.db.dependencies import get_async_db
from app.api.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationResponse
)
from app.game_state.services.geography.location_service import LocationService
from app.game_state.services.geography.location_type_service import LocationTypeService
from app.api.routes.location.location_route_utils import build_location_response

router = APIRouter()

# ——— Reusable id+name ref ———
class RefModel(BaseModel):
    id: UUID
    name: str

    # allow populating from attributes (i.e. ORM .id/.name)
    model_config = ConfigDict(from_attributes=True)


# ——— Full Location context schema ———
class LocationFullSchema(BaseModel):
    # raw columns
    id:              UUID
    name:            str
    description:     Optional[str]
    base_danger_level: int
    attributes:      Dict[str, Any]
    is_active:       bool
    tags:            List[str]
    created_at:      datetime
    updated_at:      Optional[datetime]

    # one‐to‐one relationships, nested
    world:            Optional[RefModel]
    location_type:    RefModel
    parent:           Optional[RefModel]
    parent_type:      Optional[RefModel]
    theme:            Optional[RefModel]
    biome:            Optional[RefModel]
    sub_type:         Optional[RefModel]
    controlling_faction: Optional[RefModel]

    # collections as lists of Refs
    resource_nodes:  List[RefModel] = []

    # allow populating from attributes (i.e. ORM .world/.resource_nodes etc.)
    model_config = ConfigDict(from_attributes=True)

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

    locations = await location_service.find_all()

    return [await build_location_response(loc, location_service) for loc in locations]


@router.get("/{location_id}", response_model=LocationFullSchema)
async def get_location(
    location_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a location by ID."""
    location_service = LocationService(db)
    location = await location_service.find_by_id_full(location_id)

    location_response = LocationFullSchema.model_validate(location)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location_response


@router.post("/", response_model=LocationResponse)
async def create_location(
    location_data: LocationCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new location."""
    location_service = LocationService(db)
    try:
        location = await location_service.create_location(location_data.model_dump(exclude_unset=True))
        return location
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