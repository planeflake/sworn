# --- START OF FILE app/game_state/entities/_template_entity.py ---
# Rename this file to match your specific entity (e.g., building_entity.py, item_entity.py)

# --- Core Python Imports ---
import uuid
from uuid import UUID,uuid4
import enum
from datetime import datetime, date, time # Import date/time types as needed
from typing import Optional, List, Dict, Any # For Python type hinting
from dataclasses import dataclass, field    # Core dataclass tools

# --- Import Domain Enums & Other Domain Entities ---
# Define or import Enums relevant to this domain entity
# from app.game_state.enums import ExampleStatusEnum # Example import
class Slot(enum.Enum):
    #Armour slots
    HEAD = "ACTIVE"
    SHOULDERS = "SHOULDERS"
    CHEST = "INACTIVE"
    HANDS = "HANDS"
    WRISTS = "WRISTS"
    WAIST = "WAIST"
    LEGS = "LEGS"
    FEET = "FEET"

    #Jewelry slots
    NECK = "NECK"
    FINGER = "FINGER"
    TRINKET = "TRINKET"

    #Cloak
    BACK = "BACK"

    #Weapon slots
    MAIN_HAND = "MAIN_HAND"
    OFF_HAND = "OFF_HAND"
    TWO_HAND = "TWO_HAND"

    #Quick slots
    QUICK_SLOT_1 = "QUICK_SLOT_1"
    QUICK_SLOT_2 = "QUICK_SLOT_2"
    QUICK_SLOT_3 = "QUICK_SLOT_3"
    QUICK_SLOT_4 = "QUICK_SLOT_4"
    QUICK_SLOT_5 = "QUICK_SLOT_5"

# Define or import other domain entities this entity might contain/reference
# Use relative imports if they are in the same 'entities' folder
# from .related_entity import RelatedEntity # Example import
@dataclass
class RelatedEntity: # Placeholder definition
    entity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = "Related"

# --- Base Entity (Optional but Recommended) ---
# Assume you have a base domain entity like this defined in entities/base.py:
# @dataclass
# class BaseEntity:
#     entity_id: uuid.UUID = field(default_factory=uuid.uuid4)
#     name: str = "Unnamed Entity"
# If using a base entity, import and inherit from it:
from .base import BaseEntity # Assuming entities/base.py exists
from app.game_state.enums.shared import StatusEnum, RarityEnum


# --- Entity Definition ---
# Rename 'TemplateEntity' and adjust inheritance if needed
@dataclass
class Item(BaseEntity):  # Inherit from your domain BaseEntity
    """
    ITEM TEMPLATE (@dataclass).
    Represents the internal state and data for core game logic.
    """
    # --- Override BaseEntity Fields ---
    entity_id: UUID = field(default_factory=uuid4, init=False)  # Exclude from constructor
    name: str = field(default="Unnamed Entity", init=False)  # Exclude from constructor

    # --- Required Fields (Specific to this Entity) ---
    slot: str  # Must be provided on creation

    # --- Optional Basic Types ---
    description: Optional[str] = None
    count: Optional[int] = None
    value: Optional[float] = None
    is_important: bool = False

    # --- Domain Enum ---
    status: StatusEnum = StatusEnum.ACTIVE
    rarity: RarityEnum = RarityEnum.COMMON
    for_sale_at: Optional[UUID] = None
    base_price: Optional[float] = None
    reputation_modifier: Optional[float] = None

    # --- Date/Time Fields ---
    event_timestamp: Optional[datetime] = None
    start_date: Optional[date] = None

    # --- Complex Types ---
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    related_entities: List[RelatedEntity] = field(default_factory=list)

    # --- Links to other Entities ---
    related_entity_id: Optional[uuid.UUID] = None

    # --- Timestamps ---
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# --- END OF FILE app/game_state/entities/_template_entity.py ---