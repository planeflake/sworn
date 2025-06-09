from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from app.db.dependencies import get_async_db
from app.game_state.repositories.action_category_repository import ActionCategoryRepository
from app.game_state.repositories.action_template_repository import ActionTemplateRepository
from app.game_state.managers.action_category_manager import ActionCategoryManager
from app.game_state.managers.action_template_manager import ActionTemplateManager
from app.api.schemas.action_template_schema import (
    ActionCategoryCreateSchema,
    ActionCategoryUpdateSchema,
    ActionCategoryResponseSchema,
    ActionTemplateCreateSchema,
    ActionTemplateUpdateSchema,
    ActionTemplateResponseSchema,
    AvailableActionsQuerySchema
)

router = APIRouter(prefix="/action-templates", tags=["Action Templates"])


# Action Category Routes
@router.post("/categories", response_model=ActionCategoryResponseSchema)
async def create_action_category(
    category_data: ActionCategoryCreateSchema,
    db_session=Depends(get_async_db)
):
    """Create a new action category."""
    category_entity = ActionCategoryManager.create_category(
        name=category_data.name,
        parent_category_id=category_data.parent_category_id,
        description=category_data.description,
        icon=category_data.icon,
        display_order=category_data.display_order
    )
    
    repository = ActionCategoryRepository(db_session)
    created_category = await repository.create(category_entity)
    
    return ActionCategoryResponseSchema(**created_category.model_dump())


@router.get("/categories", response_model=List[ActionCategoryResponseSchema])
async def get_action_categories(
    parent_id: Optional[UUID] = Query(None, description="Filter by parent category ID"),
    db_session=Depends(get_async_db)
):
    """Get action categories, optionally filtered by parent."""
    repository = ActionCategoryRepository(db_session)
    
    if parent_id is None:
        categories = await repository.get_root_categories()
    else:
        categories = await repository.get_children_of_category(parent_id)
    
    return [ActionCategoryResponseSchema(**cat.model_dump()) for cat in categories]


@router.get("/categories/{category_id}", response_model=ActionCategoryResponseSchema)
async def get_action_category(
    category_id: UUID,
    include_children: bool = Query(False, description="Include child categories"),
    db_session=Depends(get_async_db)
):
    """Get a specific action category."""
    repository = ActionCategoryRepository(db_session)
    
    if include_children:
        category = await repository.get_category_with_children(category_id)
    else:
        category = await repository.get_by_id(category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Action category not found")
    
    return ActionCategoryResponseSchema(**category.model_dump())


@router.patch("/categories/{category_id}", response_model=ActionCategoryResponseSchema)
async def update_action_category(
    category_id: UUID,
    update_data: ActionCategoryUpdateSchema,
    db_session=Depends(get_async_db)
):
    """Update an action category."""
    repository = ActionCategoryRepository(db_session)
    
    category = await repository.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Action category not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    updated_category = await repository.update(category_id, update_dict)
    
    return ActionCategoryResponseSchema(**updated_category.model_dump())


@router.delete("/categories/{category_id}")
async def delete_action_category(
    category_id: UUID,
    db_session=Depends(get_async_db)
):
    """Delete an action category."""
    repository = ActionCategoryRepository(db_session)
    
    success = await repository.delete(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Action category not found")
    
    return {"message": "Action category deleted successfully"}


# Action Template Routes
@router.post("/", response_model=ActionTemplateResponseSchema)
async def create_action_template(
    template_data: ActionTemplateCreateSchema,
    db_session=Depends(get_async_db)
):
    """Create a new action template."""
    template_entity = ActionTemplateManager.create_template(
        name=template_data.name,
        category_id=template_data.category_id,
        description=template_data.description,
        action_verb=template_data.action_verb,
        requirements=template_data.requirements,
        possible_rewards=template_data.possible_rewards,
        base_duration_seconds=template_data.base_duration_seconds,
        difficulty_level=template_data.difficulty_level,
        max_skill_level=template_data.max_skill_level,
        icon=template_data.icon,
        flavor_text=template_data.flavor_text,
        display_order=template_data.display_order,
        is_repeatable=template_data.is_repeatable,
        prerequisite_action_ids=template_data.prerequisite_action_ids,
        unlock_world_day=template_data.unlock_world_day
    )
    
    repository = ActionTemplateRepository(db_session)
    created_template = await repository.create(template_entity)
    
    return ActionTemplateResponseSchema(**created_template.model_dump())


@router.get("/", response_model=List[ActionTemplateResponseSchema])
async def get_action_templates(
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    skill_id: Optional[UUID] = Query(None, description="Filter by required skill"),
    db_session=Depends(get_async_db)
):
    """Get action templates with optional filters."""
    repository = ActionTemplateRepository(db_session)
    
    if category_id:
        templates = await repository.get_by_category(category_id)
    elif skill_id:
        templates = await repository.get_templates_requiring_skill(skill_id)
    else:
        templates = await repository.find_all()

    return [ActionTemplateResponseSchema(**template.model_dump()) for template in templates]


@router.get("/{template_id}", response_model=ActionTemplateResponseSchema)
async def get_action_template(
    template_id: UUID,
    db_session=Depends(get_async_db)
):
    """Get a specific action template."""
    repository = ActionTemplateRepository(db_session)
    template = await repository.get_by_id(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Action template not found")
    
    return ActionTemplateResponseSchema(**template.model_dump())


@router.patch("/{template_id}", response_model=ActionTemplateResponseSchema)
async def update_action_template(
    template_id: UUID,
    update_data: ActionTemplateUpdateSchema,
    db_session=Depends(get_async_db)
):
    """Update an action template."""
    repository = ActionTemplateRepository(db_session)
    
    template = await repository.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Action template not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    updated_template = await repository.update(template_id, update_dict)
    
    return ActionTemplateResponseSchema(**updated_template.model_dump())


@router.delete("/{template_id}")
async def delete_action_template(
    template_id: UUID,
    db_session=Depends(get_async_db)
):
    """Delete an action template."""
    repository = ActionTemplateRepository(db_session)
    
    success = await repository.delete(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Action template not found")
    
    return {"message": "Action template deleted successfully"}


@router.get("/available/for-character", response_model=List[ActionTemplateResponseSchema])
async def get_available_actions_for_character(
    character_id: UUID = Query(..., description="Character ID"),
    location_type_id: UUID = Query(..., description="Location type ID"),
    tool_tier_id: Optional[UUID] = Query(None, description="Available tool tier ID"),
    db_session=Depends(get_async_db)
):
    """
    Get action templates available to a specific character at a location.
    This would typically query character skills from the character repository.
    """
    # Note: This is simplified - in a real implementation you'd fetch character skills
    # from the character repository first
    repository = ActionTemplateRepository(db_session)
    
    # Placeholder: assuming character has no skills for this example
    character_skills = {}  # dict[UUID, int] - skill_id -> skill_level
    
    # Note: This would need to be updated to work with the new tool tier system
    # For now, return empty list until full integration is complete
    available_templates = []
    
    return [ActionTemplateResponseSchema(**template.model_dump()) for template in available_templates]