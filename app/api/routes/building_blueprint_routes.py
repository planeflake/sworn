# --- START OF FILE app/api/routes/building_blueprint_routes.py ---

import logging
from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db
from app.game_state.services.building_blueprint_service import BuildingBlueprintService # Actual service
from app.api.schemas.building_blueprint_schema import (
    BuildingBlueprintRead,
    BuildingBlueprintCreate,
    BuildingBlueprintUpdate,
)

router = APIRouter(
    prefix="/building-blueprints",
    tags=["Building Blueprints"] # This tag will group these endpoints in Swagger UI
)

# Dependency to get the service
def get_blueprint_service(db: AsyncSession = Depends(get_async_db)):
    return BuildingBlueprintService(db)


@router.post(
    "/",
    response_model=BuildingBlueprintRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Building Blueprint"
)
async def create_building_blueprint(
    blueprint_in: BuildingBlueprintCreate,
    service: BuildingBlueprintService = Depends(get_blueprint_service)
):
    """
    Create a new building blueprint, including all its stages and optional features.
    """
    try:
        created_blueprint = await service.create_blueprint(blueprint_data=blueprint_in)
        return created_blueprint
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logging.exception(f"Unexpected error creating building blueprint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")


@router.get(
    "/{blueprint_id}",
    response_model=BuildingBlueprintRead,
    summary="Get Building Blueprint by ID"
)
async def get_building_blueprint(
    blueprint_id: UUID,
    service: BuildingBlueprintService = Depends(get_blueprint_service)
):
    blueprint = await service.get_blueprint(blueprint_id)
    if not blueprint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building blueprint not found")
    return blueprint


@router.get(
    "/",
    response_model=List[BuildingBlueprintRead],
    summary="List All Building Blueprints"
)
async def list_building_blueprints(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    theme_id: Optional[UUID] = Query(None, description="Filter blueprints by theme ID"),
    service: BuildingBlueprintService = Depends(get_blueprint_service)
):
    blueprints = await service.get_all_blueprints(skip=skip, limit=limit, theme_id=theme_id)
    return blueprints

@router.put(
    "/{blueprint_id}",
    response_model=BuildingBlueprintRead,
    summary="Update Building Blueprint (Core Info)"
)
async def update_building_blueprint(
    blueprint_id: UUID,
    blueprint_in: BuildingBlueprintUpdate,
    service: BuildingBlueprintService = Depends(get_blueprint_service)
):
    """
    Update core information of a building blueprint.
    Does NOT update stages or features directly; use dedicated endpoints for those if needed.
    """
    try:
        updated_blueprint = await service.update_blueprint(blueprint_id=blueprint_id, update_data=blueprint_in)
        if not updated_blueprint:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building blueprint not found")
        return updated_blueprint
    except ValueError as e: # For validation errors from the service
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logging.exception(f"Unexpected error updating building blueprint {blueprint_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")


@router.delete(
    "/{blueprint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Building Blueprint"
)
async def delete_building_blueprint(
    blueprint_id: UUID,
    service: BuildingBlueprintService = Depends(get_blueprint_service)
):
    deleted = await service.delete_blueprint(blueprint_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building blueprint not found")
    return None

# --- END OF FILE app/api/routes/building_blueprint_routes.py ---