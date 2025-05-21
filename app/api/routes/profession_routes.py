# --- START OF FILE app/api/routes/profession_routes.py ---

from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from app.game_state.services.profession_service import ProfessionService
from app.api.schemas.profession_schema import (
    ProfessionDefinitionRead,
    ProfessionDefinitionCreate,
    ProfessionDefinitionUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db
from typing import List
from uuid import UUID, uuid4
import logging

EXAMPLE_THEME_FANTASY = uuid4()
EXAMPLE_THEME_MEDIEVAL = uuid4()

create_example_body = {
    "summary": "Example Blacksmith", 
    "description": "A basic example for creating a Blacksmith profession definition.",
    "value": {
        "name": "blacksmith_common",
        "display_name": "Blacksmith",
        "description": "A craftsman who forges metal items like tools and weapons.",
        "category": "CRAFTING",
        "skill_requirements": [
            {"skill_id": "forging", "level": 3},
            {"skill_id": "strength", "level": 5}
        ],
        "available_theme_ids": [str(EXAMPLE_THEME_FANTASY), str(EXAMPLE_THEME_MEDIEVAL)], 
        "valid_unlock_methods": ["npc_teacher", "item_manual"],
        "unlock_condition_details": [
            {"type": "npc_teacher", "target_id": "master_blacksmith_prof_id"},
            {"type": "item_manual", "target_id": "item_basic_smithing_guide"}  
        ],
        "python_class_override": None, 
        "archetype_handler": "GenericCrafter", 
        "configuration_data": { 
            "recipes_known": ["dagger_iron", "horseshoe"],
            "tool_required": "hammer_smithing",
            "workbench_required": "forge_basic"
        }
    }
}

create_example_body_innkeeper = {
    "summary": "Example Innkeeper",
    "description": "Example for creating an Innkeeper profession definition.",
    "value": {
        "name": "innkeeper_generic",
        "display_name": "Innkeeper",
        "description": "Manages a tavern, serves drinks, offers lodging, and gathers rumors.",
        "category": "SERVICE",
        "skill_requirements": [
            {"skill_id": "social", "level": 4},
            {"skill_id": "bartering", "level": 2}
        ],
        "available_theme_ids": [str(EXAMPLE_THEME_FANTASY), str(EXAMPLE_THEME_MEDIEVAL)],
        "valid_unlock_methods": ["npc_teacher"],
        "unlock_condition_details": [
            {"type": "npc_teacher", "target_id": "veteran_innkeeper_prof_id"}
        ],
        "python_class_override": "InnkeeperSpecificLogic",
        "archetype_handler": None,
        "configuration_data": {
            "max_lodging_capacity_base": 5,
            "rumor_gather_chance": 0.15
        }
    }
}

router = APIRouter(
)

@router.post(
    "/",
    response_model=ProfessionDefinitionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Profession Definition",
)
async def create_profession_definition(
    profession_in: ProfessionDefinitionCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Creates a new profession definition (blueprint).

    - Requires a unique **name** (internal identifier).
    - Define skill requirements, themes, unlock methods, and configuration.
    """
    service = ProfessionService(db)
    try:
        created_profession = await service.create_profession(profession_data=profession_in)
        return created_profession
    except ValueError as e:
        logging.warning(f"Validation error creating profession: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logging.exception(f"Unexpected error creating profession definition: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

@router.get(
    "/",
    response_model=List[ProfessionDefinitionRead],
    summary="List Profession Definitions",
)
async def list_profession_definitions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max number of records to return"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retrieves a list of profession definitions with pagination.
    """
    service = ProfessionService(db)
    professions = await service.get_all_professions(skip=skip, limit=limit)
    return professions

@router.get(
    "/{profession_id}",
    response_model=ProfessionDefinitionRead,
    summary="Get Profession Definition by ID",
)
async def get_profession_definition(
    profession_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Retrieves a specific profession definition by its UUID.
    """
    service = ProfessionService(db)
    profession = await service.get_profession(profession_id)
    if not profession:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profession definition not found")
    return profession

@router.put(
    "/{profession_id}",
    response_model=ProfessionDefinitionRead,
    summary="Update Profession Definition",
)
async def update_profession_definition(
    profession_id: UUID,
    profession_in: ProfessionDefinitionUpdate = Body(...),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Updates an existing profession definition. Send only the fields to update.
    """
    service = ProfessionService(db)
    updated_profession = await service.update_profession(profession_id=profession_id, update_data=profession_in)
    if not updated_profession:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profession definition not found")
    return updated_profession

@router.delete(
    "/{profession_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Profession Definition",
)
async def delete_profession_definition(
    profession_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Deletes a profession definition by its UUID.
    """
    service = ProfessionService(db)
    deleted = await service.delete_profession(profession_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profession definition not found")
    # No content response on success
    return None

# --- END OF FILE app/api/routes/profession_routes.py ---