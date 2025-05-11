from app.game_state.enums.character import CharacterTypeEnum
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
import random

class CharacterRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    character_type: CharacterTypeEnum = None
    world_id: UUID
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
