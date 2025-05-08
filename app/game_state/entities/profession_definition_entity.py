# --- START OF FILE app/game_state/entities/profession_definition_entity.py ---

import uuid
from dataclasses import dataclass, field, KW_ONLY # <<< Import KW_ONLY
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import enum

from .base import BaseEntity # Import the BaseEntity

# --- Enums (if needed) ---

# Use kw_only=True for the entire class if ALL fields defined here
# should be keyword-only (simplest approach)
# Or use the '_' marker before the first keyword-only field.
@dataclass #(kw_only=True)
class ProfessionDefinitionEntity(BaseEntity):
    """
    Domain Entity representing a Profession Definition/Blueprint.
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntity.
    Uses kw_only=True for fields defined in this class.
    """
    # Inherited fields (entity_id, name) handled by BaseEntity

    # --- Keyword-Only Fields for this class ---
    # Use the KW_ONLY separator (requires Python 3.10+)
    # All fields AFTER this marker must be specified by keyword in the constructor
    _: KW_ONLY

    display_name: str # Now effectively keyword-only

    # Optional/defaulted fields can follow
    description: Optional[str] = None
    category: Optional[str] = None
    skill_requirements: List[Dict[str, Any]] = field(default_factory=list)
    available_theme_ids: List[uuid.UUID] = field(default_factory=list)
    valid_unlock_methods: List[str] = field(default_factory=list)
    unlock_condition_details: List[Dict[str, Any]] = field(default_factory=list)
    python_class_override: Optional[str] = None
    archetype_handler: Optional[str] = None
    configuration_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    # No need for __post_init__ just to set updated_at if created_at is handled okay
    # Keep __post_init__ for actual validation if needed
    # def __post_init__(self):
    #     if self.updated_at is None:
    #         self.updated_at = self.created_at

    # Inherits __repr__ from BaseEntity

# --- END OF FILE app/game_state/entities/profession_definition_entity.py ---