from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import uuid
import logging

from app.db.dependencies import get_async_db
from app.game_state.services.biome_service import BiomeService
from app.api.schemas.biome_schema import BiomeCreate, BiomeRead, BiomeUpdate
from app.api.schemas.shared import PaginatedResponse

router = APIRouter()

@router.post("/", response_model=BiomeRead)
async def create_biome(
    biome_data: BiomeCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new biome.
    
    Requires biome_id, name, and display_name at minimum.
    """
    try:
        biome_service = BiomeService(db=db)
        created_biome = await biome_service.create_biome(biome_data=biome_data)
        return created_biome
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.exception(f"Error creating biome: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/", response_model=PaginatedResponse[BiomeRead])
async def list_biomes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db)
):
    """
    List all biomes with pagination.
    """
    try:
        biome_service = BiomeService(db=db)
        return await biome_service.get_all_biomes_paginated(skip=skip, limit=limit)
    except Exception as e:
        logging.exception(f"Error retrieving biomes: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/{biome_id}", response_model=BiomeRead)
async def get_biome(
    biome_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get a biome by its UUID.
    """
    try:
        biome_service = BiomeService(db=db)
        biome = await biome_service.get_biome_by_id(biome_uuid=biome_id)
        
        if not biome:
            raise HTTPException(status_code=404, detail=f"Biome with ID {biome_id} not found")
        
        return biome
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Error retrieving biome: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/by-biome-id/{string_id}", response_model=BiomeRead)
async def get_biome_by_string_id(
    string_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get a biome by its string identifier (e.g., 'forest', 'desert').
    """
    try:
        biome_service = BiomeService(db=db)
        biome = await biome_service.get_biome_by_string_id(biome_id=string_id)
        
        if not biome:
            raise HTTPException(status_code=404, detail=f"Biome with string ID '{string_id}' not found")
        
        return biome
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Error retrieving biome: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.put("/{biome_id}", response_model=BiomeRead)
async def update_biome(
    biome_id: uuid.UUID,
    update_data: BiomeUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update an existing biome.
    """
    try:
        biome_service = BiomeService(db=db)
        updated_biome = await biome_service.update_biome(biome_uuid=biome_id, update_data=update_data)
        
        if not updated_biome:
            raise HTTPException(status_code=404, detail=f"Biome with ID {biome_id} not found")
        
        return updated_biome
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Error updating biome: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.delete("/{biome_id}", response_model=Dict[str, Any])
async def delete_biome(
    biome_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Delete a biome.
    """
    try:
        biome_service = BiomeService(db=db)
        result = await biome_service.delete_biome(biome_uuid=biome_id)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Biome with ID {biome_id} not found")
        
        return {"success": True, "message": f"Biome with ID {biome_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Error deleting biome: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/danger-level/{level}", response_model=List[BiomeRead])
async def get_biomes_by_danger_level(
    level: int = Path(..., ge=1, le=5),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get biomes with the specified danger level (1-5).
    """
    try:
        biome_service = BiomeService(db=db)
        biomes = await biome_service.get_biomes_by_danger_level(danger_level=level)
        return biomes
    except Exception as e:
        logging.exception(f"Error retrieving biomes by danger level: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/movement/range", response_model=List[BiomeRead])
async def get_biomes_by_movement_range(
    min_modifier: float = Query(..., ge=0.0, le=2.0),
    max_modifier: float = Query(..., ge=0.0, le=2.0),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get biomes within a specific movement modifier range.
    """
    if min_modifier > max_modifier:
        raise HTTPException(status_code=400, detail="min_modifier must be less than or equal to max_modifier")
    
    try:
        biome_service = BiomeService(db=db)
        biomes = await biome_service.get_biomes_by_movement_range(
            min_modifier=min_modifier, 
            max_modifier=max_modifier
        )
        return biomes
    except Exception as e:
        logging.exception(f"Error retrieving biomes by movement range: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")