# --- START OF FILE app/api/routes/skill_definition_routes.py ---

import logging
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_async_db
from app.game_state.services.skill_definition_service import SkillDefinitionService
from app.api.schemas.skill_definition_schema import (
    SkillDefinitionRead,
    SkillDefinitionCreate,
    SkillDefinitionUpdate,
)

router = APIRouter(
)

# Define an example for creation
create_skill_example = {
    "summary": "Example Mining Skill",
    "description": "A basic example for creating a Mining skill definition.",
    "value": {
        "name": "Mining",
        "description": "The ability to extract ores and minerals from rock.",
        "max_level": 100,
        "themes": ["fantasy", "medieval", "sci-fi", "post-apocalyptic"],
        "metadata": {
            "xp_curve": "standard",
            "base_yield_multiplier": 1.0
        }
    }
}

@router.post("/skill-definitions", response_model=SkillDefinitionRead, status_code=status.HTTP_201_CREATED)
async def create_skill_definition(
    skill_in: SkillDefinitionCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Create a new skill definition.

    This endpoint creates a new entry in the skill definition registry using
    the provided `SkillDefinitionCreate` schema. Each skill must have a unique `name`.

    Parameters:
    ----------
    - skill_in (SkillDefinitionCreate): The input data for the skill definition, including name, description, and any other required fields.
    - db (AsyncSession): SQLAlchemy async database session dependency, injected automatically.

    Returns:
    -------
    - SkillDefinitionRead: A representation of the newly created skill definition including its ID and other persisted fields.

    Raises:
    -------
    - HTTPException (400): If the input validation fails or a skill with the same name already exists.
    - HTTPException (500): If an unexpected server-side error occurs during creation.

    Example Request Body:
    {
        "name": "blacksmithing",
        "description": "The ability to forge and shape metal items."
    }
    """
    service = SkillDefinitionService(db)
    try:
        created_skill_def = await service.create_skill_definition(skill_data=skill_in)
        return created_skill_def
    except ValueError as e:
        logging.warning(f"Validation error creating skill definition: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logging.exception(f"Unexpected error creating skill definition: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error."
        )


@router.get(
    "/",
    response_model=List[SkillDefinitionRead],
    summary="List Skill Definitions",
)
async def list_skill_definitions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_async_db),
):
    """Retrieves a list of skill definitions."""
    service = SkillDefinitionService(db)
    skill_defs = await service.get_all_skill_definitions(skip=skip, limit=limit)
    return skill_defs

@router.get(
    "/{skill_definition_id}",
    response_model=SkillDefinitionRead,
    summary="Get Skill Definition by ID",
)
async def get_skill_definition(
    skill_definition_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Retrieves a specific skill definition by its UUID."""
    service = SkillDefinitionService(db)
    skill_def = await service.get_skill_definition(skill_definition_id)
    if not skill_def:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill definition not found")
    return skill_def

@router.put(
    "/{skill_definition_id}",
    response_model=SkillDefinitionRead,
    summary="Update Skill Definition",
)
async def update_skill_definition(
    skill_definition_id: UUID,
    skill_in: SkillDefinitionUpdate = Body(...),
    db: AsyncSession = Depends(get_async_db),
):
    """Updates an existing skill definition."""
    service = SkillDefinitionService(db)
    updated_skill_def = await service.update_skill_definition(
        skill_definition_id=skill_definition_id, update_data=skill_in
    )
    if not updated_skill_def:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill definition not found")
    return updated_skill_def

@router.delete(
    "/{skill_definition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Skill Definition",
)
async def delete_skill_definition(
    skill_definition_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Deletes a skill definition by its UUID."""
    service = SkillDefinitionService(db)
    deleted = await service.delete_skill_definition(skill_definition_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill definition not found")
    return None

# --- END OF FILE app/api/routes/skill_definition_routes.py ---