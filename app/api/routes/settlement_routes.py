from fastapi import APIRouter, Depends, HTTPException, status # Added status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db
import logging
from pydantic import BaseModel, Field, ConfigDict # Added Field
import random
from app.game_state.services.core.world_service import WorldService
from app.game_state.services.settlement_service import SettlementService
from uuid import UUID
from typing import Optional, Dict # Added Dict for resource quantities
from datetime import datetime

# --- Pydantic Models ---

class SettlementRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    world_id: UUID
    population: int
    resources: Dict[str, int] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Pydantic V2 config (replaces V1's class Config)
    model_config = ConfigDict(
        from_attributes=True  # Replaces orm_mode = True
    )

class SettlementCreate(BaseModel):
    """Request model for creating a Settlement"""
    world_id: UUID = Field(..., description="The ID of the world where the settlement will be created.")
    name: Optional[str] = Field(default=None, min_length=3, max_length=100, description="The name of the settlement. Auto-generated if not provided.")
    description: Optional[str] = Field(default=None, max_length=500, description="A description for the settlement.")
    population: Optional[int] = Field(default=10, ge=1, description="The initial population of the settlement.")
    resources: Optional[Dict[str,int]] = Field(default_factory=dict, description="A dict of resource IDs to add to the settlement.")

    # Pydantic V2 config for schema examples
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Riverside",
                    "description": "A quiet village by the river.",
                    "world_id": "d376bc6a-d9c6-40b4-91d6-78bf398e1bfb", # Example UUID
                    "population": 10,
                    "resources": [
                        {
                            "resource_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                            "quantity": 10
                        }
                    ]
                },
                {
                    # Example for auto-generated name (client sends world_id only)
                    "world_id": "9368e202-a217-464c-953d-78ea89dacb01",
                    "description": "A newly discovered outpost."
                }
            ]
        }
    )

class SettlementCreatedResponse(BaseModel):
    """Response model for Settlement creation"""
    settlement: SettlementRead
    message: str

class SettlementOutputResponse(BaseModel):
     """Response model for Settlement output"""
     settlement: SettlementRead 
     message: str

     model_config = ConfigDict(
         from_attributes=True
     )

# --- Router ---
router = APIRouter()

@router.post(
    "/",
    response_model=SettlementCreatedResponse,
    status_code=status.HTTP_201_CREATED, # Use 201 for successful creation
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
        created_settlement_entity: SettlementRead = await settlement_service.create( # Corrected service call
            name=name_to_create,
            description=settlement_data.description,
            world_id=settlement_data.world_id,
            population=settlement_data.population, # if your service method expects it
            resources=settlement_data.resources # if your service method expects it
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
        
class ResourceAddRequest(BaseModel):
    """Request model for adding a resource to a settlement."""
    resource_id: UUID = Field(..., description="The UUID of the resource to add.")
    quantity: int = Field(1, ge=1, description="The quantity of the resource to add. Defaults to 1.")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "resource_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                    "quantity": 10
                }
            ]
        }
    }
    
@router.post(
    "/{settlement_id}/resources",
    response_model=SettlementOutputResponse
)
async def add_resource_to_settlement(
    settlement_id: UUID,
    resource_data: ResourceAddRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Add a quantity of a specific resource to a settlement.
    
    - **settlement_id**: UUID of the settlement.
    - **resource_id**: UUID of the resource to add.
    - **quantity**: Amount of the resource to add (must be >= 1).
    """
    try:
        settlement_service = SettlementService(db=db)
        updated_settlement = await settlement_service.add_resource(
            settlement_id=settlement_id,
            resource_id=resource_data.resource_id,
            quantity=resource_data.quantity
        )
        
        if not updated_settlement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Settlement with ID '{settlement_id}' not found."
            )
            
        return SettlementOutputResponse(
            settlement=updated_settlement,
            message=f"Successfully added {resource_data.quantity} of resource {resource_data.resource_id} to settlement."
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Error adding resource to settlement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the resource."
        )
        
class ResourceRemoveRequest(BaseModel):
    """Request model for removing a resource from a settlement."""
    resource_id: UUID = Field(..., description="The UUID of the resource to remove.")
    quantity: int = Field(1, ge=1, description="The quantity of the resource to remove. Defaults to 1.")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "resource_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                    "quantity": 5
                }
            ]
        }
    }
    
@router.delete(
    "/{settlement_id}/resources",
    response_model=SettlementOutputResponse
)
async def remove_resource_from_settlement(
    settlement_id: UUID,
    resource_data: ResourceRemoveRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Remove a quantity of a specific resource from a settlement.
    
    - **settlement_id**: UUID of the settlement.
    - **resource_id**: UUID of the resource to remove.
    - **quantity**: Amount of the resource to remove (must be >= 1).
    """
    try:
        settlement_service = SettlementService(db=db)
        updated_settlement = await settlement_service.remove_resource(
            settlement_id=settlement_id,
            resource_id=resource_data.resource_id,
            quantity=resource_data.quantity
        )
        
        if not updated_settlement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Settlement with ID '{settlement_id}' not found or not enough resources available."
            )
            
        return SettlementOutputResponse(
            settlement=updated_settlement,
            message=f"Successfully removed {resource_data.quantity} of resource {resource_data.resource_id} from settlement."
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Error removing resource from settlement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while removing the resource."
        )
        
@router.get(
    "/{settlement_id}/resources",
    response_model=Dict[str, int]
)
async def get_settlement_resources(
    settlement_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get all resources and their quantities in a settlement.
    
    - **settlement_id**: UUID of the settlement.
    """
    try:
        settlement_service = SettlementService(db=db)
        resources = await settlement_service.get_available_resources(settlement_id)
        
        if resources is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Settlement with ID '{settlement_id}' not found."
            )
            
        # Convert UUID keys to strings for JSON serialization
        resources_str = {str(k): v for k, v in resources.items()}
            
        return resources_str
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Error getting settlement resources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving resources."
        )

class LeaderAssignRequest(BaseModel):
    """Request model for assigning a leader to a settlement."""
    leader_id: UUID = Field(..., description="The UUID of the character to assign as the leader.")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "leader_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
                }
            ]
        }
    }

@router.put(
    "/{settlement_id}/leader",
    response_model=SettlementOutputResponse
)
async def assign_leader_to_settlement(
    settlement_id: UUID,
    leader_data: LeaderAssignRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Assign a character as the leader of a settlement.
    
    - **settlement_id**: UUID of the settlement to modify.
    - **leader_id**: UUID of the character to assign as the leader.
    """
    try:
        settlement_service = SettlementService(db=db)
        updated_settlement = await settlement_service.set_leader(
            settlement_id=settlement_id,
            leader_id=leader_data.leader_id
        )
        
        if not updated_settlement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Settlement with ID '{settlement_id}' not found."
            )
            
        return SettlementOutputResponse(
            settlement=updated_settlement,
            message=f"Successfully assigned leader {leader_data.leader_id} to settlement."
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"Error assigning leader to settlement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while assigning the leader."
        )

