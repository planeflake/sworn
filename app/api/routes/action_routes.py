from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from datetime import datetime, timedelta

from app.db.dependencies import get_async_db
from app.api.schemas.action_schema import (
    CreateActionRequest, 
    ActionResponse, 
    UpdateActionRequest,
    ActionListResponse
)
from app.game_state.entities.action.character_action_pydantic import ActionStatus
from app.game_state.repositories.action_repository import ActionRepository
from app.game_state.repositories.character_repository import CharacterRepository  
from app.game_state.managers.action_manager import ActionManager
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/characters", tags=["actions"])

async def get_action_repository(db: AsyncSession = Depends(get_async_db)) -> ActionRepository:
    """Dependency to get action repository."""
    return ActionRepository(db)

async def get_character_repository(db: AsyncSession = Depends(get_async_db)) -> CharacterRepository:
    """Dependency to get character repository."""
    return CharacterRepository(db)

async def get_action_manager(action_repo: ActionRepository = Depends(get_action_repository)) -> ActionManager:
    """Dependency to get action manager."""
    return ActionManager(action_repo)

@router.post("/{character_id}/actions", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def create_character_action(
    character_id: UUID,
    action_request: CreateActionRequest,
    action_manager: ActionManager = Depends(get_action_manager),
    character_repo: CharacterRepository = Depends(get_character_repository),
    action_repo: ActionRepository = Depends(get_action_repository)
):
    """
    Create a new action for a character.
    
    This endpoint allows players to assign tasks to their characters such as:
    - Gathering resources from resource nodes
    - Building structures using blueprints  
    - Crafting items at workshops
    - Trading with NPCs or other players
    """
    # Verify character exists
    character = await character_repo.find_by_id(character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    # Calculate duration if not provided
    duration = action_request.duration
    if duration is None:
        duration = action_manager.estimate_action_duration(
            character_id=character_id,
            action_type=action_request.action_type,
            parameters=action_request.parameters
        )
    
    # Create action entity
    action = action_manager.create_action(
        name=action_request.name,
        character_id=character_id,
        action_type=action_request.action_type,
        location_id=action_request.location_id,
        duration=duration,
        target_id=action_request.target_id,
        parameters=action_request.parameters
    )
    
    # Save to database
    saved_action = await action_repo.save(action)
    
    # Calculate estimated completion time
    response = ActionResponse.model_validate(saved_action)
    if saved_action.start_time:
        response.estimated_completion = saved_action.start_time + timedelta(seconds=saved_action.duration)
    
    return response

@router.get("/{character_id}/actions", response_model=ActionListResponse)
async def get_character_actions(
    character_id: UUID,
    action_repo: ActionRepository = Depends(get_action_repository),
    character_repo: CharacterRepository = Depends(get_character_repository)
):
    """
    Get all actions for a character.
    
    Returns both active and completed actions, with counts for easy filtering.
    """
    # Verify character exists
    character = await character_repo.find_by_id(character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found"
        )
    
    # Get all actions for character
    actions = await action_repo.get_actions_by_character(character_id)
    
    # Convert to response models with estimated completion times
    action_responses = []
    active_count = 0
    
    for action in actions:
        response = ActionResponse.model_validate(action)
        
        # Calculate estimated completion time for active actions
        if action.start_time and action.status == ActionStatus.IN_PROGRESS:
            response.estimated_completion = action.start_time + timedelta(seconds=action.duration)
        
        # Count active actions
        if action.status in [ActionStatus.QUEUED, ActionStatus.IN_PROGRESS]:
            active_count += 1
            
        action_responses.append(response)
    
    return ActionListResponse(
        actions=action_responses,
        total=len(action_responses),
        active_count=active_count
    )

@router.get("/{character_id}/actions/{action_id}", response_model=ActionResponse)
async def get_character_action(
    character_id: UUID,
    action_id: UUID,
    action_repo: ActionRepository = Depends(get_action_repository)
):
    """Get a specific action for a character."""
    action = await action_repo.find_by_id(action_id)
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action with ID {action_id} not found"
        )
    
    if action.character_id != character_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action does not belong to the specified character"
        )
    
    response = ActionResponse.model_validate(action)
    
    # Calculate estimated completion time
    if action.start_time and action.status == ActionStatus.IN_PROGRESS:
        response.estimated_completion = action.start_time + timedelta(seconds=action.duration)
    
    return response

@router.patch("/{character_id}/actions/{action_id}", response_model=ActionResponse)
async def update_character_action(
    character_id: UUID,
    action_id: UUID,
    update_request: UpdateActionRequest,
    action_manager: ActionManager = Depends(get_action_manager),
    action_repo: ActionRepository = Depends(get_action_repository)
):
    """
    Update an existing character action.
    
    Typically used by the game engine to update progress, status, and results.
    Players can also use this to cancel actions.
    """
    # Get existing action
    action = await action_repo.find_by_id(action_id)
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action with ID {action_id} not found"
        )
    
    if action.character_id != character_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action does not belong to the specified character"
        )
    
    # Build update data
    update_data = {}
    if update_request.name is not None:
        update_data['name'] = update_request.name
    if update_request.status is not None:
        update_data['status'] = update_request.status
    if update_request.progress is not None:
        update_data['progress'] = update_request.progress
    if update_request.result is not None:
        update_data['result'] = update_request.result
    
    # Update timestamps based on status changes
    if update_request.status == ActionStatus.IN_PROGRESS and not action.start_time:
        update_data['start_time'] = datetime.now()
    elif update_request.status in [ActionStatus.COMPLETED, ActionStatus.FAILED, ActionStatus.CANCELLED]:
        update_data['end_time'] = datetime.now()
        if update_request.progress is None:
            update_data['progress'] = 1.0 if update_request.status == ActionStatus.COMPLETED else action.progress
    
    # Apply updates
    for key, value in update_data.items():
        setattr(action, key, value)
    
    setattr(action, 'updated_at', datetime.now())
    
    # Save updated action
    saved_action = await action_repo.save(action)
    
    # Return response with estimated completion
    response = ActionResponse.model_validate(saved_action)
    if saved_action.start_time and saved_action.status == ActionStatus.IN_PROGRESS:
        response.estimated_completion = saved_action.start_time + timedelta(seconds=saved_action.duration)
    
    return response

@router.delete("/{character_id}/actions/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_character_action(
    character_id: UUID,
    action_id: UUID,
    action_repo: ActionRepository = Depends(get_action_repository)
):
    """
    Cancel a character action.
    
    Only works for queued or in-progress actions. Completed/failed actions cannot be cancelled.
    """
    action = await action_repo.find_by_id(action_id)
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action with ID {action_id} not found"
        )
    
    if action.character_id != character_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action does not belong to the specified character"
        )
    
    if action.status not in [ActionStatus.QUEUED, ActionStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel action with status: {action.status}"
        )
    
    # Update action to cancelled
    action.status = ActionStatus.CANCELLED
    action.end_time = datetime.now()
    action.updated_at = datetime.now()
    
    await action_repo.save(action)