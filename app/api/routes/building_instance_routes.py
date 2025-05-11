# --- START OF FILE app/api/routes/building_instance_routes.py ---

import logging
from uuid import UUID
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db # Your DB session dependency
from app.game_state.services.building_instance_service import BuildingInstanceService
from app.api.schemas.building_instance import (
    BuildingInstanceRead,
    BuildingInstanceCreate,
    BuildingInstanceUpdate,
)

router = APIRouter()

# Example body for creation - adapt with real UUIDs from your system
EXAMPLE_BLUEPRINT_ID = uuid.uuid4()
EXAMPLE_SETTLEMENT_ID = uuid.uuid4()

create_example_body = {
    "name": "The Rusty Bucket Inn",
    "building_blueprint_id": str(EXAMPLE_BLUEPRINT_ID),
    "settlement_id": str(EXAMPLE_SETTLEMENT_ID),
    "level": 1,
    "status": "UNDER_CONSTRUCTION", # Will be set by service logic usually
    "current_hp": 50,
    "max_hp": 200,
    "construction_progress": 0.1,
    "current_stage_number": 1
}

@router.post(
    "/",
    response_model=BuildingInstanceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Building Instance"
)
async def create_building_instance(
    building_in: BuildingInstanceCreate = Body(..., examples={"default": {"summary": "New Inn", "value": create_example_body}}),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new building instance in a settlement.
    Typically called when a player initiates construction.
    """
    service = BuildingInstanceService(db)
    try:
        created_building = await service.create_building_instance(creation_data=building_in)
        return created_building
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logging.exception(f"Unexpected error creating building instance: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

@router.get(
    "/{instance_id}",
    response_model=BuildingInstanceRead,
    summary="Get Building Instance by ID"
)
async def get_building_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    service = BuildingInstanceService(db)
    building = await service.get_building_instance(instance_id)
    if not building:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building instance not found")
    return building

@router.get(
    "/settlement/{settlement_id}",
    response_model=List[BuildingInstanceRead],
    summary="List Building Instances in a Settlement"
)
async def list_buildings_in_settlement(
    settlement_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_async_db)
):
    service = BuildingInstanceService(db)
    try:
        buildings = await service.list_buildings_in_settlement(settlement_id=settlement_id, skip=skip, limit=limit)
        return buildings
    except ValueError as e: # e.g. settlement not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put(
    "/{instance_id}",
    response_model=BuildingInstanceRead,
    summary="Update Building Instance"
)
async def update_building_instance(
    instance_id: UUID,
    building_in: BuildingInstanceUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    service = BuildingInstanceService(db)
    try:
        updated_building = await service.update_building_instance(instance_id=instance_id, update_data=building_in)
        if not updated_building:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building instance not found")
        return updated_building
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete(
    "/{instance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Building Instance"
)
async def delete_building_instance(
    instance_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    service = BuildingInstanceService(db)
    deleted = await service.delete_building_instance(instance_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building instance not found")
    return None

# Example of a more complex action endpoint
@router.post(
    "/{instance_id}/advance-construction",
    response_model=BuildingInstanceRead,
    summary="Advance Construction of a Building Stage"
)
async def advance_building_construction(
    instance_id: UUID,
    progress_delta: float = Body(..., gt=0, le=1.0, embed=True, description="Amount of progress made (0.0 to 1.0)."),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Simulates game tick or player action advancing construction.
    This would typically be called by game loop logic or specific events.
    """
    service = BuildingInstanceService(db)
    try:
        building = await service.advance_stage_construction(instance_id=instance_id, progress_delta=progress_delta)
        return building
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logging.exception(f"Error advancing construction for building {instance_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")


# --- END OF FILE app/api/routes/building_instance_routes.py ---