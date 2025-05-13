# --- START OF FILE app/api/routes/building_upgrade_blueprint_routes.py ---

import logging
from uuid import UUID, uuid4
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db
from app.game_state.services.building_upgrade_blueprint_service import BuildingUpgradeBlueprintService
from app.api.schemas.building_upgrade_blueprint_schema import (
    BuildingUpgradeBlueprintRead,
    BuildingUpgradeBlueprintCreate,
    BuildingUpgradeBlueprintUpdate,
)

router = APIRouter()

# Example for creation
example_stone_tower_bp_id = str(uuid4()) # Placeholder
example_wood_resource_id = str(uuid4())
example_mason_profession_id = str(uuid4())

create_upgrade_bp_example = {
    "summary": "Arrow Slits for Stone Tower",
    "value": {
        "name": "stone_tower_arrow_slits_v1",
        "display_name": "Add Arrow Slits",
        "description": "Enhances a stone tower with defensive arrow slits.",
        "target_blueprint_criteria": {"base_blueprint_id": example_stone_tower_bp_id, "min_level": 1},
        "prerequisites": {"required_tech": "basic_fortifications"},
        "resource_cost": {example_wood_resource_id: 50},
        "profession_cost": {example_mason_profession_id: 1},
        "duration_days": 2,
        "effects": {"adds_feature": "arrow_slits", "defense_bonus": 5},
        "is_initial_choice": True,
    }
}

@router.post("/", response_model=BuildingUpgradeBlueprintRead, status_code=status.HTTP_201_CREATED)
async def create_building_upgrade_blueprint(
    upgrade_bp_in: BuildingUpgradeBlueprintCreate = Body(..., examples={"arrow_slits": create_upgrade_bp_example}),
    db: AsyncSession = Depends(get_async_db),
):
    """Creates a new building upgrade blueprint."""
    service = BuildingUpgradeBlueprintService(db)
    try:
        created_bp = await service.create_upgrade_blueprint(data=upgrade_bp_in)
        return created_bp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logging.exception(f"Error creating building upgrade blueprint: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

# --- Add GET (list, one), PUT, DELETE routes similar to other routers ---
@router.get("/", response_model=List[BuildingUpgradeBlueprintRead])
async def list_building_upgrade_blueprints(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200), db: AsyncSession = Depends(get_async_db)
):
    service = BuildingUpgradeBlueprintService(db)
    return await service.get_all_upgrade_blueprints(skip=skip, limit=limit)

@router.get("/{blueprint_id}", response_model=BuildingUpgradeBlueprintRead)
async def get_building_upgrade_blueprint(blueprint_id: UUID, db: AsyncSession = Depends(get_async_db)):
    service = BuildingUpgradeBlueprintService(db)
    bp = await service.get_upgrade_blueprint(blueprint_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building upgrade blueprint not found")
    return bp

@router.put("/{blueprint_id}", response_model=BuildingUpgradeBlueprintRead)
async def update_building_upgrade_blueprint(
    blueprint_id: UUID,
    upgrade_bp_in: BuildingUpgradeBlueprintUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    service = BuildingUpgradeBlueprintService(db)
    updated_bp = await service.update_upgrade_blueprint(blueprint_id, upgrade_bp_in)
    if not updated_bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building upgrade blueprint not found")
    return updated_bp

@router.delete("/{blueprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_building_upgrade_blueprint(blueprint_id: UUID, db: AsyncSession = Depends(get_async_db)):
    service = BuildingUpgradeBlueprintService(db)
    deleted = await service.delete_upgrade_blueprint(blueprint_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building upgrade blueprint not found")
    return None

# --- END OF FILE app/api/routes/building_upgrade_blueprint_routes.py ---