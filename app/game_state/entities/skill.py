# --- START OF FILE app/game_state/entities/_template_entity.py ---
# Rename this file to match your specific entity (e.g., building_entity.py, item_entity.py)

# --- Core Python Imports ---
import uuid
import enum
from datetime import datetime, date, time # Import date/time types as needed
from typing import Optional, List, Dict, Any # For Python type hinting
from dataclasses import dataclass, field    # Core dataclass tools

# --- Import Domain Enums & Other Domain Entities ---
# Define or import Enums relevant to this domain entity
# from app.game_state.enums import ExampleStatusEnum # Example import
class ExampleStatusEnum(enum.Enum): # Placeholder definition
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

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

# --- Entity Definition ---
# Rename 'TemplateEntity' and adjust inheritance if needed
@dataclass
class SkillEntity(BaseEntity):  # Inherit from your domain BaseEntity if applicable
    """
    Skill TEMPLATE (@dataclass).
    Represents the internal state and data for core game logic.
    """
    # --- Required Fields (Specific to this Entity) ---
    level: str  # Example: must be provided on creation

    # --- Optional Basic Types ---
    description: Optional[str] = None
    count: Optional[int] = None
    value: Optional[float] = None
    is_important: bool = False  # Example with a simple default

    # --- Domain Enum ---
    status: ExampleStatusEnum = ExampleStatusEnum.ACTIVE  # Default value

    # --- Date/Time Fields ---
    event_timestamp: Optional[datetime] = None
    start_date: Optional[date] = None

    # --- Complex Types (Dictionaries, Lists of Primitives, Lists of Entities) ---
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    related_entities: List[RelatedEntity] = field(default_factory=list)  # List of other domain entities

    # --- Links to other Entities (by ID) ---
    related_entity_id: Optional[uuid.UUID] = None

    # --- Timestamps (Usually Optional in Domain, set by Repo/DB) ---
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # --- Override BaseEntity Fields ---
    entity_id: uuid.UUID = field(default_factory=uuid.uuid4, init=False)
    name: str = field(default="Unnamed Entity", init=False)

# --- END OF FILE app/game_state/entities/_template_entity.py ---