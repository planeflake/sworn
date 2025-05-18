# --- START OF FILE app/game_state/schemas/profession_schema.py ---

import uuid
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Optional: Import Enums if you want to use them directly in Schemas for validation
#from app.game_state.enums.profession import ProfessionCategory, ProfessionUnlockType

class ProfessionDefinitionBase(BaseModel):
    """Base schema for common profession definition fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Unique internal name/ID.")
    display_name: str = Field(..., min_length=1, max_length=100, description="User-facing name.")
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50, description="Profession category (e.g., CRAFTING).") # Or use Enum
    skill_requirements: List[Dict[str, Any]] = Field(default_factory=list, description="E.g., [{'skill_id': 'mining', 'level': 5}]")
    available_theme_ids: List[uuid.UUID] = Field(default_factory=list)
    valid_unlock_methods: List[str] = Field(default_factory=list, description="List of allowed unlock method names (e.g., 'npc_teacher').") # Or use List[ProfessionUnlockType]
    unlock_condition_details: List[Dict[str, Any]] = Field(default_factory=list, description="Specific details for unlocks (e.g., which NPC/item).")
    python_class_override: Optional[str] = Field(None, max_length=100)
    archetype_handler: Optional[str] = Field(None, max_length=100)
    configuration_data: Dict[str, Any] = Field(default_factory=dict)


class ProfessionDefinitionCreate(ProfessionDefinitionBase):
    """Schema for creating a new profession definition."""
    # Inherits all fields from Base
    # Add any specific creation-only fields if necessary
    pass


class ProfessionDefinitionUpdate(ProfessionDefinitionBase):
    """Schema for updating a profession definition. All fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    # Make lists/dicts optional on update, or require full replacement
    skill_requirements: Optional[List[Dict[str, Any]]] = None
    available_theme_ids: Optional[List[uuid.UUID]] = None
    valid_unlock_methods: Optional[List[str]] = None
    unlock_condition_details: Optional[List[Dict[str, Any]]] = None
    configuration_data: Optional[Dict[str, Any]] = None


class ProfessionDefinitionRead(ProfessionDefinitionBase):
    """Schema for reading/returning a profession definition."""
    id: uuid.UUID # Use 'id' here matching the BaseRepository's conversion expectation
    # name: str # Already in Base
    # display_name: str # Already in Base
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = { # Pydantic v2+
        "from_attributes": True # Enable ORM mode / create from attributes
    }


# --- END OF FILE app/game_state/schemas/profession_schema.py ---