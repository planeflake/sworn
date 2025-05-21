# --- START OF FILE app/game_state/entities/_template_entity.py ---
# Rename this file, e.g., settlement_building.py, character.py, item.py

# --- Core Python Imports ---
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone # Use timezone-aware datetimes
from typing import Optional, List, Dict, Any # For type hinting
import enum                     # For defining status or type enums

# --- Project Imports ---
from .base import BaseEntity    # <<< Import the BaseEntity

# --- Define Enums specific to this Entity (or import from a central enums file) ---
class TemplateEntityStatus(enum.Enum):
    UNKNOWN = "UNKNOWN"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"

# --- Domain Entity Definition ---
# Rename 'DomainEntityTemplate' to your specific entity name (e.g., SettlementBuilding, GameItem)
@dataclass
class DomainEntityTemplate(BaseEntity): # <<< Inherit from BaseEntity
    """
    Template for a Domain Entity using Python dataclasses.
    Inherits 'entity_id' and 'name' from BaseEntity.
    Represents the state of a core concept within the game's domain logic layer.

    NOTE: Inherited fields:
     - entity_id: UUID (from BaseEntity)
     - name: str (from BaseEntity, defaults to "Unnamed Entity")
    """

    # --- Specific Attributes for this Entity ---
    # id and name are inherited from BaseEntity - DO NOT REDEFINE HERE

    # Integer attribute, e.g., quantity, level, count.
    level: int = 1 # Example with a default value

    # Optional longer text description (could override/supplement BaseEntity's name).
    description: Optional[str] = None

    # Floating point attribute, e.g., weight, modifier, progress (0.0-1.0).
    modifier: Optional[float] = None

    # Boolean flag.
    is_enabled: bool = True # Example with a default value

    # --- Enum for State/Type ---
    # Uses the Enum defined above. Default value is good practice.
    status: TemplateEntityStatus = TemplateEntityStatus.ACTIVE

    # --- Date/Time Attributes ---
    # created_at/updated_at are now handled by BaseEntity, no need to declare them here

    # --- Collections ---
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # --- Relationships (Represented by ID) ---
    # Remember: Use BaseEntity's 'entity_id' when referring to other entities.
    parent_entity_id: uuid.UUID
    owner_character_id: Optional[uuid.UUID] = None

    # --- Initialization Logic ---
    def __post_init__(self):
        """
        Called automatically after the dataclass is initialized.
        The BaseEntity __post_init__ (if defined) is NOT called automatically.
        Call super().__post_init__() if needed.
        """
        # BaseEntity now handles created_at and updated_at
        
        # Example: Basic validation for fields specific to this entity.
        if self.level < 1:
            raise ValueError(f"Level cannot be less than 1 for {self.name} ({self.entity_id})") # Use inherited fields

        # We no longer need to set updated_at, it's handled by BaseEntity


    # --- Representation ---
    # __repr__ is inherited from BaseEntity.
    # If you need to add more info, override it like this:
    # def __repr__(self) -> str:
    #     base_repr = super().__repr__() # Get the parent's repr string
    #     # Find the closing parenthesis of the base repr
    #     closing_paren_index = base_repr.rfind(')')
    #     # Add specific fields before the closing parenthesis
    #     specifics = f", level={self.level}, status={self.status.name}"
    #     return base_repr[:closing_paren_index] + specifics + base_repr[closing_paren_index:]


    # --- Domain Logic Methods ---
    # As discussed, keep these simple or move to Managers/Services.
    # Methods can now access inherited 'self.entity_id' and 'self.name'.


# --- END OF FILE app/game_state/entities/_template_entity.py ---