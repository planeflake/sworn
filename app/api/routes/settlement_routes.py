from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db 
import logging
from pydantic import BaseModel
import random
from app.game_state.services.world_service import WorldService
from app.game_state.models.settlement import SettlementEntity
from app.game_state.services.settlement_service import SettlementService
from uuid import UUID
from typing import Optional
from datetime import datetime

class SettlementRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    world_id: UUID
    population: int
    resources: Optional[list]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class SettlementCreatedResponse(BaseModel):
    """Response model for Settlement creation"""
    settlement: SettlementRead
    message: str

class SettlementOutputResponse(BaseModel):
    """Response model for Settlement output"""
    settlement: SettlementEntity
    message: str

router = APIRouter()

@router.post("/settlements", response_model=SettlementCreatedResponse)
async def create_settlement(
        settlement_name: str = Body(..., embed=True),
        settlement_description: Optional[str] = Body(...,embed=True),
        world_id: str = Body(..., embed=True),
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Create a new Settlement with the given ID in the specified world.
    
    If Settlement_id is not provided, a random UUID will be generated.
    If Settlement_name is not provided, a random test Settlement name will be generated.
    f.eks "test_Settlement_123"
    If Settlement_description is not provided, it will be set to None.
    """
    try:

        # Validate world_id format (UUID)
        world_service = WorldService(db=db)
        world_exists = await world_service.exists(world_id=world_id)
        if not world_exists:
            raise HTTPException(status_code=404, detail="Invalid world ID provided.")
            
        # Generate random Settlement name if not provided
        if settlement_name is None:
            settlement_name = f"test_Settlement_{random.randint(1, 1000)}"
        
        settlement_service = SettlementService(db=db)

        # SettlementService.create_Settlement must be async and take AsyncSession
        settlement = await SettlementService.create(
            settlement_service,
            name=settlement_name,
            description=settlement_description,
            world_id=world_id
        )
        
        # Return the response
        return SettlementCreatedResponse(
            settlement=settlement, 
            message="Settlement created successfully"
        )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error creating Settlement: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")