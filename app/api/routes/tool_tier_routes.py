from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from app.db.dependencies import get_async_db
from app.game_state.services.items.tool_tier_service import ToolTierService
from app.game_state.repositories.tool_tier_repository import ToolTierRepository
from app.game_state.managers.tool_tier_manager import ToolTierManager
from app.api.schemas.tool_tier_schema import (
    ToolTierCreateSchema,
    ToolTierUpdateSchema,
    ToolTierResponseSchema,
    ThemeProgressionCreateSchema,
    ToolTierProgressionResponseSchema
)

router = APIRouter(prefix="/tool-tiers", tags=["Tool Tiers"])


@router.post("/", response_model=ToolTierResponseSchema)
async def create_tool_tier(
    tier_data: ToolTierCreateSchema,
    db_session=Depends(get_async_db)
):
    """Create a new tool tier."""
    tier_entity = ToolTierManager.create_tool_tier(
        name=tier_data.name,
        theme_id=tier_data.theme_id,
        tier_name=tier_data.tier_name,
        tier_level=tier_data.tier_level,
        effectiveness_multiplier=tier_data.effectiveness_multiplier,
        description=tier_data.description,
        icon=tier_data.icon,
        required_tech_level=tier_data.required_tech_level,
        required_materials=tier_data.required_materials,
        flavor_text=tier_data.flavor_text,
        color_hex=tier_data.color_hex
    )
    
    repository = ToolTierRepository(db_session)
    created_tier = await repository.create(tier_entity)
    
    return ToolTierResponseSchema(**created_tier.model_dump())


@router.get("/", response_model=List[ToolTierResponseSchema])
async def get_tool_tiers(
    theme_id: Optional[UUID] = Query(None, description="Filter by theme ID"),
    tier_level: Optional[int] = Query(None, description="Filter by tier level"),
    tech_level: Optional[int] = Query(None, description="Filter by available tech level"),
    db_session=Depends(get_async_db)
):
    """Get tool tiers with optional filters."""
    tool_tier_service = ToolTierService(db_session)
    
    tool_tiers = await tool_tier_service.find_all()
    
    return [ToolTierResponseSchema(**tier.model_dump()) for tier in tool_tiers]


@router.get("/progressions/{theme_id}", response_model=ToolTierProgressionResponseSchema)
async def get_theme_progression(
    theme_id: UUID,
    db_session=Depends(get_async_db)
):
    """Get the complete tool tier progression for a theme."""
    repository = ToolTierRepository(db_session)
    tiers = await repository.get_progression_for_theme(theme_id)
    
    if not tiers:
        raise HTTPException(status_code=404, detail="No tool tiers found for theme")
    
    return ToolTierProgressionResponseSchema(
        theme_id=theme_id,
        theme_name="Unknown",  # Would typically fetch from theme repository
        tiers=[ToolTierResponseSchema(**tier.model_dump()) for tier in tiers],
        total_tiers=len(tiers)
    )


@router.post("/progressions", response_model=ToolTierProgressionResponseSchema)
async def create_theme_progression(
    progression_data: ThemeProgressionCreateSchema,
    db_session=Depends(get_async_db)
):
    """Create a complete tool tier progression for a theme."""
    # Create the progression using the manager
    tier_entities = ToolTierManager.create_theme_progression(
        progression_data.theme_id,
        progression_data.theme_name
    )
    
    # Save all tiers to database
    repository = ToolTierRepository(db_session)
    created_tiers = []
    for tier_entity in tier_entities:
        created_tier = await repository.create(tier_entity)
        created_tiers.append(created_tier)
    
    return ToolTierProgressionResponseSchema(
        theme_id=progression_data.theme_id,
        theme_name=progression_data.theme_name,
        tiers=[ToolTierResponseSchema(**tier.model_dump()) for tier in created_tiers],
        total_tiers=len(created_tiers)
    )


@router.get("/{tier_id}", response_model=ToolTierResponseSchema)
async def get_tool_tier(
    tier_id: UUID,
    db_session=Depends(get_async_db)
):
    """Get a specific tool tier."""
    repository = ToolTierRepository(db_session)
    tier = await repository.find_by_id(tier_id)
    
    if not tier:
        raise HTTPException(status_code=404, detail="Tool tier not found")
    
    return ToolTierResponseSchema(**tier.model_dump())


@router.patch("/{tier_id}", response_model=ToolTierResponseSchema)
async def update_tool_tier(
    tier_id: UUID,
    update_data: ToolTierUpdateSchema,
    db_session=Depends(get_async_db)
):
    """Update a tool tier."""
    repository = ToolTierRepository(db_session)
    
    tier = await repository.find_by_id(tier_id)
    if not tier:
        raise HTTPException(status_code=404, detail="Tool tier not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    updated_tier = await repository.update(tier_id, update_dict)
    
    return ToolTierResponseSchema(**updated_tier.model_dump())


@router.delete("/{tier_id}")
async def delete_tool_tier(
    tier_id: UUID,
    db_session=Depends(get_async_db)
):
    """Delete a tool tier."""
    repository = ToolTierRepository(db_session)
    
    success = await repository.delete(tier_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tool tier not found")
    
    return {"message": "Tool tier deleted successfully"}


@router.get("/themes/{theme_id}/max-tier", response_model=ToolTierResponseSchema)
async def get_max_tier_for_theme(
    theme_id: UUID,
    db_session=Depends(get_async_db)
):
    """Get the highest tier available for a theme."""
    repository = ToolTierRepository(db_session)
    tier = await repository.get_max_tier_for_theme(theme_id)
    
    if not tier:
        raise HTTPException(status_code=404, detail="No tiers found for theme")
    
    return ToolTierResponseSchema(**tier.model_dump())


@router.get("/themes/{theme_id}/basic-tier", response_model=ToolTierResponseSchema)
async def get_basic_tier_for_theme(
    theme_id: UUID,
    db_session=Depends(get_async_db)
):
    """Get the basic (tier 1) tool tier for a theme."""
    repository = ToolTierRepository(db_session)
    tier = await repository.get_basic_tier_for_theme(theme_id)
    
    if not tier:
        raise HTTPException(status_code=404, detail="No basic tier found for theme")
    
    return ToolTierResponseSchema(**tier.model_dump())