from app.game_state.services.character_service import CharacterService
from app.game_state.enums.character import CharacterTypeEnum
from app.api.schemas.character import CharacterCreate, CharacterTraitsUpdate, AddCharacterTraits
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db 
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID
import random
import logging

class CharacterRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    character_type: Optional[CharacterTypeEnum] = None
    world_id: UUID
    theme_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": f"test_Character_{random.randint(1, 1000)}",
                "world_id": "9368e202-a217-464c-953d-78ea89dacb01",
                "description": "test character",
            }
        }
    )

class CharacterCreatedResponse(BaseModel):
    """Response model for Character creation"""
    id: UUID
    name: str
    description: str
    character_type: CharacterTypeEnum
    world_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "Character": {
                    "name": f"test_Character_{random.randint(1, 1000)}",
                    "world_id": "9368e202-a217-464c-953d-78ea89dacb01",
                    "description": "test character",
                },
                "message": "Character created successfully"
            }
        }
    )

class CharacterOutputResponse(BaseModel):
    """Response model for character output"""
    character: CharacterRead
    message: str

router = APIRouter()

@router.get("/{character_id}", response_model=CharacterOutputResponse)
async def get_character(
        character_id: UUID,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Get a character by its ID.
    
    If the character is not found, a 404 error will be raised.
    """
    try:
        character_service = CharacterService(db=db)
        character = await character_service.get_by_id(character_id=character_id)
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found.")
        
        return CharacterOutputResponse(
            character=character, 
            message="Character retrieved successfully"
        )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error retrieving character: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/player/{player_id}", response_model=list[CharacterOutputResponse])
async def get_characters_by_player(
        player_id: UUID,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Get all characters for a given player ID.
    
    If no characters are found, an empty list will be returned.
    """
    try:
        character_service = CharacterService(db=db)
        characters = await character_service.get_by_player(player_id=player_id)
        
        if not characters:
            return []
        
        return [CharacterOutputResponse(character=character, message="Characters retrieved successfully") for character in characters]
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error retrieving characters by player: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.post("/") #, response_model=CharacterCreatedResponse)
async def create_character(
        character_data: CharacterCreate,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Create a new character with the given ID in the specified world.
    
    If character_id is not provided, a random UUID will be generated.
    If character_name is not provided, a random test character name will be generated.
    f.eks "test_character_123"
    If character_description is not provided, it will be set to None.
    """
    try:
        character_service = CharacterService(db)
        character = await character_service.create_character(character_data=character_data)

        logging.info(f"Creating character: {character}")
        # Return the response
        return character
        # Commented out due to unreachable code
        # return CharacterCreatedResponse(
        #     character=character, 
        #     message="Character created successfully"
        # )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error creating character: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
@router.post("/{character_id}/add_resources")
async def add_resources_to_character(
        character_id: UUID,
        resources: list,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Add resources to a character by its ID.
    
    If the character is not found, a 404 error will be raised.
    """
    try:
        character_service = CharacterService(db=db)
        character = await character_service.get_by_id(character_id=character_id)
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found.")
        
        # Add resources to the character
        await character_service.add_resources(character_id=character_id, resources=resources)
        
        return {"message": "Resources added successfully."}
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error adding resources to character: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/{character_id}/traits")
async def get_character_traits(
        character_id: UUID,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Get a character's traits by its ID.
    
    If the character is not found, a 404 error will be raised.
    """
    try:
        character_service = CharacterService(db=db)
        character = await character_service.get_by_id(character_id=character_id)
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found.")
        
        # Get the character's traits
        traits = await character_service.get_character_traits(character_id=character_id)
        
        return {"traits": [trait.value for trait in traits]}
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error getting character traits: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.put("/{character_id}/traits")
async def update_character_traits(
        character_id: UUID,
        traits_data: CharacterTraitsUpdate,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Replace all of a character's traits with the provided list.
    
    If the character is not found, a 404 error will be raised.
    """
    try:
        character_service = CharacterService(db=db)
        character = await character_service.get_by_id(character_id=character_id)
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found.")
        
        # Update the character's traits
        updated_character = await character_service.update_traits(character_id=character_id, traits_data=traits_data)
        
        if not updated_character:
            raise HTTPException(status_code=404, detail="Failed to update character traits.")
        
        return {"message": "Character traits updated successfully.", "character": updated_character}
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error updating character traits: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
        
@router.post("/{character_id}/traits")
async def add_character_traits(
        character_id: UUID,
        traits_data: AddCharacterTraits,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Add one or more traits to a character, preserving existing traits.
    
    If the character is not found, a 404 error will be raised.
    
    Example:
    ```json
    {
        "traits": ["STRATEGIC", "EXPANSIVE"]
    }
    ```
    """
    try:
        character_service = CharacterService(db=db)
        character = await character_service.get_by_id(character_id=character_id)
        
        if not character:
            raise HTTPException(status_code=404, detail="Character not found.")
        
        # Add traits to the character
        updated_character = await character_service.add_traits(character_id=character_id, traits_data=traits_data)
        
        if not updated_character:
            raise HTTPException(status_code=404, detail="Failed to add character traits.")
        
        return {"message": "Traits added to character successfully.", "character": updated_character}
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error adding character traits: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")