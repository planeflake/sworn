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
class SkillEntity(BaseEntity): # Inherit from your domain BaseEntity if applicable
    """
    Skill TEMPLATE (@dataclass).
    Represents the internal state and data for core game logic.
    """
    # --- Override/Use Base Fields ---
    # entity_id and name might be inherited from BaseEntity.
    # If BaseEntity doesn't have defaults, provide them or make them required here.
    # Example overriding inherited defaults if needed (usually not necessary):
    # entity_id: uuid.UUID = field(default_factory=uuid.uuid4)
    # name: str = "Default Template Name"

    # --- Required Fields (Specific to this Entity) ---
    # Fields without defaults MUST come before fields with defaults
    # (unless using KW_ONLY)
    level: str # Example: must be provided on creation

    # --- Optional Basic Types ---
    # Use Optional[...] for fields that can be None
    description: Optional[str] = None
    count: Optional[int] = None
    value: Optional[float] = None
    is_important: bool = False # Example with a simple default

    # --- Domain Enum ---
    status: ExampleStatusEnum = ExampleStatusEnum.ACTIVE # Default value

    # --- Date/Time Fields ---
    # Often optional, populated during logic or persistence
    event_timestamp: Optional[datetime] = None
    start_date: Optional[date] = None

    # --- Complex Types (Dictionaries, Lists of Primitives, Lists of Entities) ---
    # Use default_factory for mutable types!
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    related_entities: List[RelatedEntity] = field(default_factory=list) # List of other domain entities

    # --- Links to other Entities (by ID) ---
    # Store the UUID of the related entity
    related_entity_id: Optional[uuid.UUID] = None

    # --- Timestamps (Usually Optional in Domain, set by Repo/DB) ---
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # --- Dataclass Configuration ---
    # @dataclass arguments (optional):
    # init=True (default): generate __init__
    # repr=True (default): generate __repr__
    # eq=True (default): generate __eq__
    # order=False (default): set True to generate comparison methods (__lt__, etc.)
    # unsafe_hash=False (default): set True to generate __hash__ if __eq__ is True (or implement manually)
    # frozen=False (default): set True to make instances immutable after creation

    # --- Domain Logic Methods (Optional) ---
    # Keep these focused on the entity's own state/rules.
    # Complex orchestration belongs in Services/Managers.
    # def update_status(self, new_status: ExampleStatusEnum):
    #     # Example logic
    #     if self.status != ExampleStatusEnum.DELETED:
    #          self.status = new_status

# --- END OF FILE app/game_state/entities/_template_entity.py ---