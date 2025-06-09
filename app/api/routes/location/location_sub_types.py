"""
API routes for location subtypes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db
from app.game_state.services.geography.location_sub_type_service import LocationSubTypeService
from app.api.schemas.location.location_sub_types import LocationSubtypeCreate, LocationSubtypeUpdate
from app.game_state.entities.geography.location_sub_type import LocationSubtype


router = APIRouter()

@router.post("/", response_model=LocationSubtype, status_code=status.HTTP_201_CREATED)
async def create_location_subtype(
    subtype_data: LocationSubtypeCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new location subtype"""
    service = LocationSubTypeService(db)
    try:
        return await service.create_subtype(subtype_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{subtype_id}", response_model=LocationSubtype)
async def get_location_subtype(
    subtype_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get location subtype by ID"""
    service = LocationSubtypeService(db)
    subtype = await service.get_subtype_by_id(subtype_id)
    if not subtype:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location subtype not found")
    return subtype


@router.get("/code/{code}", response_model=LocationSubtype)
async def get_location_subtype_by_code(
    code: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get location subtype by code"""
    service = LocationSubtypeService(db)
    subtype = await service.get_subtype_by_code(code)
    if not subtype:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location subtype not found")
    return subtype


@router.put("/{subtype_id}", response_model=LocationSubtype)
async def update_location_subtype(
    subtype_id: UUID,
    update_data: LocationSubtypeUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update location subtype"""
    service = LocationSubtypeService(db)
    try:
        updated_subtype = await service.update_subtype(subtype_id, update_data)
        if not updated_subtype:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location subtype not found")
        return updated_subtype
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{subtype_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location_subtype(
    subtype_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete location subtype"""
    service = LocationSubtypeService(db)
    success = await service.delete_subtype(subtype_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location subtype not found")


@router.get("/", response_model=Dict[str, Any])
async def search_location_subtypes(
    location_type_id: Optional[UUID] = Query(None),
    theme_id: Optional[UUID] = Query(None),
    rarity: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    match_all_tags: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """Search location subtypes with filters and pagination"""
    service = LocationSubtypeService(db)
    return await service.search_subtypes(
        location_type_id=location_type_id,
        theme_id=theme_id,
        rarity=rarity,
        tags=tags,
        match_all_tags=match_all_tags,
        skip=skip,
        limit=limit
    )


@router.get("/location-type/{location_type_id}", response_model=List[LocationSubtype])
async def get_subtypes_by_location_type(
    location_type_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get all subtypes for a specific location type"""
    service = LocationSubtypeService(db)
    return await service.get_subtypes_by_location_type(location_type_id)


@router.get("/theme/{theme_id}", response_model=List[LocationSubtype])
async def get_subtypes_by_theme(
    theme_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get all subtypes for a specific theme"""
    service = LocationSubtypeService(db)
    return await service.get_subtypes_by_theme(theme_id)


@router.get("/location-type/{location_type_id}/theme/{theme_id}", response_model=List[LocationSubtype])
async def get_subtypes_by_location_type_and_theme(
    location_type_id: UUID,
    theme_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get subtypes for specific location type and theme combination"""
    service = LocationSubtypeService(db)
    return await service.get_subtypes_by_location_type_and_theme(location_type_id, theme_id)


@router.get("/rarity/{rarity}", response_model=List[LocationSubtype])
async def get_subtypes_by_rarity(
    rarity: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get subtypes by rarity level"""
    service = LocationSubtypeService(db)
    return await service.get_subtypes_by_rarity(rarity)


@router.post("/bulk", response_model=List[LocationSubtype], status_code=status.HTTP_201_CREATED)
async def bulk_create_location_subtypes(
    subtypes_data: List[LocationSubtypeCreate],
    db: AsyncSession = Depends(get_async_db)
):
    """Bulk create location subtypes"""
    service = LocationSubtypeService(db)
    try:
        return await service.bulk_create_subtypes(subtypes_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))