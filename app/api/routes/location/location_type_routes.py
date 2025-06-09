"""
API routes for location types.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.location import (
    LocationTypeCreate,
    LocationTypeUpdate,
    LocationTypeResponse
)
from app.game_state.services.geography.location_type_service import LocationTypeService
from app.db.dependencies import get_async_db

router = APIRouter()

@router.get("/", response_model=List[LocationTypeResponse])
async def get_location_types(
    theme: Optional[str] = Query(None, description="Filter by theme"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all location types, optionally filtered by theme."""
    service = LocationTypeService(db)
    types = await service.get_all_types(theme)
    return types

@router.get("/{type_id}", response_model=LocationTypeResponse)
async def get_location_type(
    type_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a location type by ID."""
    service = LocationTypeService(db)
    type_entity = await service.get_type(type_id)
    if not type_entity:
        raise HTTPException(status_code=404, detail="Location type not found")
    return type_entity

@router.get("/code/{code}", response_model=LocationTypeResponse)
async def get_location_type_by_code(
    code: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a location type by code."""
    service = LocationTypeService(db)
    type_entity = await service.get_type_by_code(code)
    if not type_entity:
        raise HTTPException(status_code=404, detail="Location type not found")
    return type_entity

@router.post("/", response_model=LocationTypeResponse)
async def create_location_type(
    type_data: LocationTypeCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new location type."""
    service = LocationTypeService(db)
    try:
        type_entity = await service.create_type(type_data.model_dump(exclude_unset=True))
        return type_entity.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{type_id}", response_model=LocationTypeResponse)
async def update_location_type(
    type_id: UUID,
    type_data: LocationTypeUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update an existing location type."""
    service = LocationTypeService(db)
    try:
        type_entity = await service.update_type(
            type_id,
            type_data.model_dump(exclude_unset=True)
        )
        if not type_entity:
            raise HTTPException(status_code=404, detail="Location type not found")
        return type_entity.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{type_id}")
async def delete_location_type(
    type_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a location type if not in use."""
    service = LocationTypeService(db)
    success = await service.delete_type(type_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete location type because it is in use by one or more locations"
        )
    return {"detail": "Location type deleted successfully"}