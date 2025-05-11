from app.game_state.services.character_service import CharacterService
from app.game_state.models.character import CharacterApiModel
from app.game_state.enums.character import CharacterTypeEnum
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db 
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID
import random
import logging

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

class CharacterCreate(BaseModel):
    """Request model for creating a Character"""
    world_id: UUID
    name: str = None
    character_type: str = None
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": f"test_Character_{random.randint(1, 1000)}",
                "world_id": "9368e202-a217-464c-953d-78ea89dacb01",
                "character_type": "npc",
                "description": "test character",
            }
        }

class CharacterCreatedResponse(BaseModel):
    """Response model for Character creation"""
    id: UUID
    name: str
    description: str
    character_type: CharacterTypeEnum
    world_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

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

@router.get("/{Character_id}", response_model=CharacterOutputResponse)
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

@router.get("/{player_id}", response_model=list[CharacterOutputResponse])
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

@router.post("/") #, response_model=CharacterCreatedResponse)
async def create_Character(
        Character_data: CharacterCreate,
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

        character_service = CharacterService(db)

        character = await character_service.create_character(character_data=Character_data)

        logging.info(f"Creating Character: {character}")
        # Return the response
        return character
        return CharacterCreatedResponse(
            Character=character, 
            message="Character created successfully"
        )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error creating Character: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
@router.post("/{Character_id}/add_resources")
async def add_resources_to_Character(
        Character_id: UUID,
        resources: list,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Add resources to a Character by its ID.
    
    If the Character is not found, a 404 error will be raised.
    """
    try:
        Character_service = CharacterService(db=db)
        Character = await Character_service.get_by_id(Character_id=Character_id)
        
        if not Character:
            raise HTTPException(status_code=404, detail="Character not found.")
        
        # Add resources to the Character
        await Character_service.add_resources(Character_id=Character_id, resources=resources)
        
        return {"message": "Resources added successfully."}
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error adding resources to Character: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")