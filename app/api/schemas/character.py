from app.game_state.enums.character import CharacterTypeEnum, CharacterTraitEnum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
import random

class CharacterRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    character_type: CharacterTypeEnum = None
    traits: List[CharacterTraitEnum] = Field(default_factory=list)
    world_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": f"test_Character_{random.randint(1, 1000)}",
                "world_id": "9368e202-a217-464c-953d-78ea89dacb01",
                "description": "test character",
                "traits": ["DEFENSIVE", "ECONOMICAL"]
            }
        }
    )

class CharacterCreate(BaseModel):
    """Request model for creating a Character"""
    world_id: UUID
    name: str = None
    character_type: CharacterTypeEnum = None
    description: Optional[str] = None
    traits: List[CharacterTraitEnum] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": f"test_Character_{random.randint(1, 1000)}",
                "world_id": "9368e202-a217-464c-953d-78ea89dacb01",
                "character_type": "NPC",
                "description": "test character",
                "traits": ["DEFENSIVE", "ECONOMICAL"]
            }
        }
    )

class CharacterTraitsUpdate(BaseModel):
    """Request model for updating a character's traits (replaces all existing traits)"""
    traits: List[CharacterTraitEnum]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "traits": ["DEFENSIVE", "ECONOMICAL", "CULTURAL"]
            }
        }
    )
        
class AddCharacterTraits(BaseModel):
    """Request model for adding one or more traits to a character (preserves existing traits)"""
    traits: List[CharacterTraitEnum]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "traits": ["STRATEGIC", "EXPANSIVE"]
            }
        }
    )

class CharacterCreatedResponse(BaseModel):
    """Response model for Character creation"""
    Character: CharacterRead
    message: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "Character": {
                    "name": f"test_Character_{random.randint(1, 1000)}",
                    "world_id": "9368e202-a217-464c-953d-78ea89dacb01",
                    "description": "test character",
                    "traits": ["DEFENSIVE", "ECONOMICAL"]
                },
                "message": "Character created successfully"
            }
        }
    )
