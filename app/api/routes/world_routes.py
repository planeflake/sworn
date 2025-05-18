# --- START OF FILE app/api/routes/world_routes.py ---

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db
import logging
from pydantic import BaseModel
import random
from app.api.schemas.world import  WorldBase, WorldCreateRequest
from app.game_state.services.world_service import WorldService
# Import ThemeService if needed for separate theme endpoints (but not directly for world creation now)
# from app.game_state.services.theme_service import ThemeService
from uuid import UUID
from typing import List, Optional
from fastapi import Query


# --- Response Models ---
class WorldResponse(BaseModel):
    """Standard response containing a world API model"""
    world: WorldBase

class WorldCreatedResponse(BaseModel):
    """Specific response for successful world creation"""
    message: str
    world: WorldBase

class AssignThemeResponse(BaseModel):
     message: str
     world: WorldBase # Include the updated world details

router = APIRouter()

@router.post(
    "/", # Path is now relative to the prefix /worlds
    response_model=WorldCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a New World",
    description="Creates a new world instance, assigning a required theme. A random name is generated if not provided."
)
async def create_world_endpoint( # Renamed for clarity
        world_data: WorldCreateRequest = Body(...),
        db: AsyncSession = Depends(get_async_db)
    ):
    """Endpoint to create a new world."""

    logging.info(f"[WorldRoutes] Request to create world with data: {world_data.model_dump()}")

    try:
        world_name = world_data.name
        if world_name is None:
            world_name = f"test_world_{random.randint(1, 1000)}"
        logging.info(f"[WorldRoutes] Request to create world '{world_name}' with Theme ID: {world_data.theme_id}")

        world_service = WorldService(db=db) # Instantiate the service (or use dependency injection if needed)



        # Call service method - it handles theme check and creation
        created_world_api_model = await world_service.create_world(
            world_data=world_data
        )

        # Service now raises specific errors or returns the model
        # Ensure the world ID is included in the response
        world_id = getattr(created_world_api_model, 'id', None)
        
        return WorldCreatedResponse(
            message="World created successfully",
            world=created_world_api_model,
            id=world_id  # Add the ID to the response
        )
    # Catch specific errors raised by the service
    except ValueError as ve:
         logging.warning(f"Validation error creating world: {ve}")
         # Check if it's a "Not Found" error vs other validation
         if "not found" in str(ve).lower():
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve)) # 400 for bad reference
         else: # Other ValueErrors (e.g., DB constraint) might be 500 or 400
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid input or constraint violation: {ve}")
    except AttributeError as ae: # Catch configuration errors (like missing entity fields)
         logging.error(f"Configuration error during world creation: {ae}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal configuration error.")
    except HTTPException: # Re-raise HTTPExceptions
        raise
    except Exception as e: # Catch unexpected errors
        logging.exception(f"Unexpected error creating world: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected internal server error occurred.")


@router.put(
    "/{world_id}/themes/{theme_id}", # Path relative to /worlds
    response_model=AssignThemeResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign Theme to World",
    description="Assigns an existing theme to an existing world."
)
async def assign_theme_to_world_endpoint(
        world_id: UUID,
        theme_id: UUID,
        db: AsyncSession = Depends(get_async_db),
    ):
    """Endpoint to assign a theme to a world."""
    try:
        logging.info(f"[WorldRoutes] Assigning theme {theme_id} to world {world_id}")

        world_service = WorldService(db=db) # Instantiate the service (or use dependency injection if needed)

        # Call the service method - it handles existence checks
        updated_world_api_model = await world_service.assign_theme_to_world(
            world_id=world_id,
            theme_id=theme_id
        )

        # Service raises ValueError if world or theme not found
        return AssignThemeResponse(
            message="Theme assigned to world successfully",
            world=updated_world_api_model
        )
    except ValueError as ve:
         logging.warning(f"Validation error assigning theme: {ve}")
         # Check if it's a "Not Found" error
         if "not found" in str(ve).lower():
              raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
         else: # Other ValueErrors (e.g., DB constraint)
              raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid input or constraint violation: {ve}")
    except AttributeError as ae: # Catch configuration errors
         logging.error(f"Configuration error assigning theme: {ae}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal configuration error.")
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Error assigning theme {theme_id} to world {world_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected internal server error occurred.")


@router.get(
    "/{world_id}", # Path relative to /worlds
    response_model=WorldResponse,
    summary="Get World by ID",
    description="Retrieves details for a specific world."
    )
async def get_world_endpoint(
        world_id: UUID,
        db: AsyncSession = Depends(get_async_db),
    ):
    """Endpoint to get a specific world."""
    world_service = WorldService(db=db) # Instantiate the service (or use dependency injection if needed)

    world_api_model = await world_service.get_world(world_id)
    if world_api_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"World {world_id} not found")
    return WorldResponse(world=world_api_model)


@router.get(
    "/", # Path relative to /worlds
    response_model=List[WorldBase],
    summary="List Worlds",
    description="Retrieves a list of all worlds, with optional pagination."
    )
async def get_all_worlds_endpoint(
        skip: int = Query(0, ge=0, description="Number of worlds to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of worlds to return"), # Added Query import needed
        db: AsyncSession = Depends(get_async_db),
    ):
    """Endpoint to get a list of worlds."""
    # Need to import Query from fastapi
    #from fastapi import Query
    world_service = WorldService(db=db) # Instantiate the service (or use dependency injection if needed)

    worlds_api_models = await world_service.get_all_worlds(skip=skip, limit=limit)
    return worlds_api_models


@router.delete(
    "/{world_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete World",
    description="Deletes a world by its ID."
)
async def delete_world_endpoint(
    world_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """Endpoint to delete a world."""
    logging.info(f"[WorldRoutes] Request to delete world {world_id}")
    world_service = WorldService(db=db) # Instantiate the service (or use dependency injection if needed)

    deleted = await world_service.delete_world(world_id)
    if not deleted:
        # Could be not found or a delete error (service logs details)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"World {world_id} not found or could not be deleted.")
    # No content to return on successful delete
    return None


# --- END OF FILE app/api/routes/world_routes.py ---