from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db 
import logging
from pydantic import BaseModel
import random
from app.game_state.services.world_service import WorldService
from app.game_state.models.character import CharacterApiModel
from app.game_state.services.character_service import CharacterService
from uuid import UUID
from typing import Optional
from datetime import datetime
import random

class CharacterRead(BaseModel):
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

        json_schema_extra = {
            "example": {
                "name": f"test_Character_{random.randint(1, 1000)}",
                "world_id": "9368e202-a217-464c-953d-78ea89dacb01",
                "description": "test character",

            }
        }

class CharacterCreatedResponse(BaseModel):
    """Response model for Character creation"""
    Character: CharacterRead
    message: str

    class config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "Character": {
                    "name": f"test_Character_{random.randint(1, 1000)}",
                    "world_id": "9368e202-a217-464c-953d-78ea89dacb01",
                    "description": "test character",
                },
                "message": "Character created successfully"
            }
        }

class CharacterOutputResponse(BaseModel):
    """Response model for Character output"""
    Character: CharacterApiModel
    message: str

router = APIRouter()

@router.get("/Characters/{Character_id}", response_model=CharacterOutputResponse)
async def get_Character(
        Character_id: UUID,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Get a Character by its ID.
    
    If the Character is not found, a 404 error will be raised.
    """
    try:
        Character_service = CharacterService(db=db)
        Character = await Character_service.get_by_id(Character_id=Character_id)
        
        if not Character:
            raise HTTPException(status_code=404, detail="Character not found.")
        
        return CharacterOutputResponse(
            Character=Character, 
            message="Character retrieved successfully"
        )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error retrieving Character: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/Characters/{player_id}", response_model=list[CharacterOutputResponse])
async def get_Characters_by_player(
        player_id: UUID,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Get all Characters for a given player ID.
    
    If no Characters are found, an empty list will be returned.
    """
    try:
        Character_service = CharacterService(db=db)
        Characters = await Character_service.get_by_player(player_id=player_id)
        
        if not Characters:
            return []
        
        return [CharacterOutputResponse(Character=Character, message="Characters retrieved successfully") for Character in Characters]
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error retrieving Characters by player: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.post("/Characters", response_model=CharacterCreatedResponse)
async def create_Character(
        Character_name: str = Body(..., embed=True),
        Character_description: Optional[str] = Body(...,embed=True),
        world_id: str = Body(..., embed=True),
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Create a new Character with the given ID in the specified world.
    
    If Character_id is not provided, a random UUID will be generated.
    If Character_name is not provided, a random test Character name will be generated.
    f.eks "test_Character_123"
    If Character_description is not provided, it will be set to None.
    """
    try:

        if world_id is None:
            logging.info("No world_id provided, using default world_id for testing.")
            world_id = "9368e202-a217-464c-953d-78ea89dacb01" # Default world ID for testing

        # Validate world_id format (UUID)
        world_service = WorldService(db=db)
        world_exists = await world_service.exists(world_id=world_id)
        if not world_exists:
            raise HTTPException(status_code=404, detail="Invalid world ID provided.")
            
        # Generate random Character name if not provided - only exists for testing.
        if Character_name is None:
            logging.info("No Character_name provided, generating a random test Character name.")
            Character_name = f"test_Character_{random.randint(1, 1000)}"
        
        Character_service = CharacterService(db=db)

        # Check if Character name already exists in the world
        existing_Character = await Character_service.get_by_name(name=Character_name, world_id=world_id)
        if existing_Character:
            raise HTTPException(status_code=400, detail="Character name already exists in the world.")

        # CharacterService.create_Character must be async and take AsyncSession
        Character = await CharacterService.create(
            Character_service,
            name=Character_name,
            description=Character_description,
            world_id=world_id
        )
        
        # Return the response
        return CharacterCreatedResponse(
            Character=Character, 
            message="Character created successfully"
        )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error creating Character: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")