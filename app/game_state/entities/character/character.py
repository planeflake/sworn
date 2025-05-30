# --- START OF FILE app/game_state/entities/character.py ---

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

# --- Import Enums from the proper location ---
from app.game_state.enums.character import CharacterTypeEnum, CharacterStatusEnum, CharacterTraitEnum

# --- Import OTHER DOMAIN ENTITIES ---
# These should point to files within app/game_state/entities/
from .equipment import EquipmentEntity 
from ..skill import SkillEntity
from .stat import StatEntity
from .item import Item

@dataclass
class CharacterEntity: # Changed class name to CharacterEntity for clarity/convention
    """ Domain Entity representing a Character's state """

    # --- Fields without defaults (required on creation) ---
    # These should come first unless using KW_ONLY tricks
    name: str
    character_type: CharacterTypeEnum
    world_id: UUID
    description: Optional[str] = None
    traits: List[CharacterTraitEnum] = field(default_factory=list)

    # --- Identifier (field with default factory) ---
    entity_id: UUID = field(default_factory=uuid4)

    # --- Fields with simple defaults ---
    level: int = 1
    is_active: bool = True
    status: CharacterStatusEnum = CharacterStatusEnum.ALIVE


    # --- Complex fields: Lists of other Domain Entities ---
    stats: List[StatEntity] = field(default_factory=list)
    equipment: List[EquipmentEntity] = field(default_factory=list)
    items: List[Item] = field(default_factory=list) # Inventory
    skills: List[SkillEntity] = field(default_factory=list)

    # --- Optional Foreign Keys / Links (to other entities' IDs) ---
    player_account_id: Optional[UUID] = None
    current_location_id: Optional[UUID] = None

    # --- Timestamps (Optional, usually set later) ---
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    # (No __init__ needed - generated by @dataclass)
    # (No Config block needed - that's for Pydantic)

# --- END OF FILE app/game_state/entities/character.py ---