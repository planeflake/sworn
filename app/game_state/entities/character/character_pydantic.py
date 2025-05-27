from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

# Import Enums from the proper location
from app.game_state.enums.character import CharacterTypeEnum, CharacterStatusEnum, CharacterTraitEnum

# Import OTHER DOMAIN ENTITIES
# These reference the old dataclass versions until all are converted
from .equipment import EquipmentEntity 
from ..skill import SkillEntity
from .stat import StatEntity
from .item import Item
from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class CharacterEntityPydantic(BaseEntityPydantic):
    """ Domain Entity representing a Character's state """

    # --- Fields without defaults (required on creation) ---
    character_type: CharacterTypeEnum
    world_id: UUID
    description: Optional[str] = None
    traits: List[CharacterTraitEnum] = Field(default_factory=list)

    # --- Fields with simple defaults ---
    level: int = 1
    is_active: bool = True
    status: CharacterStatusEnum = CharacterStatusEnum.ALIVE

    # --- Complex fields: Lists of other Domain Entities ---
    # Note: Once converted, these would point to Pydantic versions
    stats: List[StatEntity] = Field(default_factory=list)
    equipment: List[EquipmentEntity] = Field(default_factory=list)
    items: List[Item] = Field(default_factory=list) # Inventory
    skills: List[SkillEntity] = Field(default_factory=list)

    # --- Optional Foreign Keys / Links (to other entities' IDs) ---
    player_account_id: Optional[UUID] = None
    current_location_id: Optional[UUID] = None

    # --- Timestamps (Optional, usually set later) ---
    # Note: created_at and updated_at are inherited from BaseEntityPydantic
    last_login: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Adventurer",
                "world_id": "9368e202-a217-464c-953d-78ea89dacb01",
                "character_type": "NPC",
                "description": "A brave adventurer",
                "traits": ["DEFENSIVE", "ECONOMICAL"]
            }
        }
    )