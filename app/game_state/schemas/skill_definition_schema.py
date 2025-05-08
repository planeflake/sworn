# --- START OF FILE app/game_state/schemas/skill_definition_schema.py ---

import uuid
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class SkillDefinitionBase(BaseModel):
    """Base schema for skill definitions."""
    name: str = Field(..., min_length=1, max_length=100, description="Unique user-facing name of the skill.")
    # skill_key: str = Field(..., min_length=1, max_length=50, description="Unique internal key for the skill.") # If using a separate key
    description: Optional[str] = None
    max_level: int = Field(100, gt=0, description="Maximum level attainable.")
    themes: List[str] = Field(default_factory=list, description="List of theme names/IDs where skill is relevant.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional skill data (e.g., XP curve).")

class SkillDefinitionCreate(SkillDefinitionBase):
    """Schema for creating a new skill definition."""
    pass

class SkillDefinitionUpdate(BaseModel):
    """Schema for updating. All fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    # skill_key: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    max_level: Optional[int] = Field(None, gt=0)
    themes: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class SkillDefinitionRead(SkillDefinitionBase):
    """Schema for reading/returning skill definitions."""
    id: uuid.UUID # From BaseRepository conversion
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = { # Pydantic v2+
        "from_attributes": True # Enable ORM mode / create from attributes
    }
    # class Config: # Pydantic v1
    #     orm_mode = True

# --- END OF FILE app/game_state/schemas/skill_definition_schema.py ---