# --- START - app/game_state/models/character.py ---

from pydantic import BaseModel, Field, field_validator, ConfigDict # Import Field for aliasing/config, field_validator if needed
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

# Assuming Enums are defined/imported (can be same as domain or separate API enums)
# Ideally from a shared location or defined specifically for the API model layer
from app.game_state.enums.character import CharacterTypeEnum, CharacterStatusEnum
# Or from app.db.models.character import CharacterTypeEnum, CharacterStatusEnum

# --- API Models for related concepts ---
# Define how related items will look in the API response.
# These might be simpler than the full Domain Entities.

class StatApiModel(BaseModel):
    name: str
    value: Any # Or be more specific like int/float if possible
    # Omit stat_id if not needed in API response

    model_config = ConfigDict(from_attributes=True) # Allow creating from StatEntity attributes

class EquipmentApiModel(BaseModel):
    slot: str
    item_name: str # Example: Show name instead of just ID
    item_id: UUID

    model_config = ConfigDict(from_attributes=True)

class ItemApiModel(BaseModel):
    item_id: UUID
    name: str
    description: Optional[str] = None
    # Might include quantity if relevant for inventory display

    model_config = ConfigDict(from_attributes=True)

class SkillApiModel(BaseModel):
    skill_id: UUID
    name: str
    level: Optional[int] = None # Example: API might show skill level

    model_config = ConfigDict(from_attributes=True)

# --- Main Character API Model ---
class CharacterApiModel(BaseModel):
    """
    API MODEL (DTO): Defines the data structure for representing
    a Character via the API (e.g., in JSON requests/responses).
    """
    # --- Exposed Identifier & Basic Info ---
    # Use 'id' for external API, map from 'entity_id' internally
    id: UUID = Field(..., validation_alias='entity_id', serialization_alias='id')
    name: str
    character_type: CharacterTypeEnum

    # --- Exposed Game State ---
    level: int
    status: CharacterStatusEnum
    is_active: bool

    # --- Exposed Complex Data (using the API Models defined above) ---
    stats: List[StatApiModel] = [] # Use the Stat API model
    equipment: List[EquipmentApiModel] = [] # Use the Equipment API model
    items: List[ItemApiModel] = Field([], alias='inventory') # Alias 'inventory' to 'items' for API
    skills: List[SkillApiModel] = [] # Use the Skill API model

    # --- Exposed Links/Metadata ---
    # Use alias if the domain entity field name is different
    current_location_id: Optional[UUID] = None
    player_account_id: Optional[UUID] = None # Expose if relevant to API user
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None # Expose if relevant

    # --- Pydantic Configuration ---
    model_config = ConfigDict(
        # Allows creating this model from attributes of another object
        # (like the CharacterEntity domain object or the Character ORM object)
        from_attributes=True,
        
        # Allows populating the model using either the field name OR its alias.
        # Crucial for making `validation_alias='entity_id'` work for the `id` field.
        populate_by_name=True
    )

        # Example: Rename all fields for JSON output automatically (e.g., camelCase)
        # def alias_generator(field_name: str) -> str:
        #     parts = field_name.split('_')
        #     return parts[0] + "".join(word.capitalize() for word in parts[1:])
        # alias_generator = alias_generator


# --- END - app/game_state/models/character.py ---