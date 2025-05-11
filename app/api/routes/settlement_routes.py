from fastapi import APIRouter, Depends, HTTPException, status # Added status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db
import logging
from pydantic import BaseModel, Field # Added Field
import random
from app.game_state.services.world_service import WorldService
from app.game_state.models.settlement import SettlementEntity # Assuming this is your ORM model
from app.game_state.services.settlement_service import SettlementService
from uuid import UUID
from typing import Optional, List # Added List for consistency
from datetime import datetime

# --- Pydantic Models ---

class SettlementRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    world_id: UUID
    population: int
    resources: Optional[List[str]] = Field(default_factory=list) # Assuming resources are strings, adjust as needed
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Pydantic V2 config (replaces V1's class Config)
    model_config = {
        "from_attributes": True  # Replaces orm_mode = True
    }

class SettlementCreate(BaseModel):
    """Request model for creating a Settlement"""
    world_id: UUID = Field(..., description="The ID of the world where the settlement will be created.")
    name: Optional[str] = Field(default=None, min_length=3, max_length=100, description="The name of the settlement. Auto-generated if not provided.")
    description: Optional[str] = Field(default=None, max_length=500, description="A description for the settlement.")

    # Pydantic V2 config for schema examples
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Riverside",
                    "description": "A quiet village by the river.",
                    "world_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef" # Example UUID
                },
                {
                    # Example for auto-generated name (client sends world_id only)
                    "world_id": "9368e202-a217-464c-953d-78ea89dacb01",
                    "description": "A newly discovered outpost."
                }
            ]
        }
    }

class SettlementCreatedResponse(BaseModel):
    """Response model for Settlement creation"""
    settlement: SettlementRead
    message: str

class SettlementOutputResponse(BaseModel):
     """Response model for Settlement output"""
     settlement: SettlementRead 
     message: str

     model_config = {
         "from_attributes": True
     }

# --- Router ---
router = APIRouter()

@router.post(
    "/settlements",
    response_model=SettlementCreatedResponse,
    status_code=status.HTTP_201_CREATED, # Use 201 for successful creation
    summary="Create a new Settlement",
    tags=["Settlements"] # For grouping in OpenAPI docs
)
async def create_settlement_endpoint( # Renamed for clarity
        settlement_data: SettlementCreate, # Correctly define input model instance
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Create a new Settlement in the specified world.

    - **world_id**: UUID of the world (required).
    - **name**: Optional. If not provided, a random test name (e.g., "test_Settlement_123") will be generated.
    - **description**: Optional.
    """
    try:
        world_service = WorldService(db=db)
        # Assuming world_service.exists takes a UUID object for world_id
        world_exists = await world_service.exists(world_id=settlement_data.world_id)
        if not world_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, # More specific than 400
                detail=f"World with ID '{settlement_data.world_id}' not found."
            )

        name_to_create = settlement_data.name
        if name_to_create is None:
            name_to_create = f"test_Settlement_{random.randint(1, 1000)}"

        settlement_service = SettlementService(db=db)

        # Assuming SettlementService.create returns an ORM instance (SettlementEntity)
        # And that SettlementRead can be created from this ORM instance (due to from_attributes)
        created_settlement_entity: SettlementEntity = await settlement_service.create( # Corrected service call
            name=name_to_create,
            description=settlement_data.description,
            world_id=settlement_data.world_id
            # Add other necessary parameters like population, resources if they are set at creation
            # For example, if they should default to 0 or empty list:
            # population=0, # if your service method expects it
            # resources=[], # if your service method expects it
        )

        # Convert ORM entity to Pydantic model for the response
        # This happens automatically if created_settlement_entity is compatible
        # with SettlementRead (due to from_attributes = True)
        # If explicit conversion is needed, you might do:
        # settlement_for_response = SettlementRead.model_validate(created_settlement_entity)
        # but FastAPI often handles this if response_model is set and types align.

        return SettlementCreatedResponse(
            settlement=created_settlement_entity, # FastAPI will try to fit this into SettlementRead
            message="Settlement created successfully"
        )
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logging.exception(f"Error creating Settlement: {e}") # Use logging.exception for stack trace
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while creating the settlement." # Avoid leaking raw error details
        )

