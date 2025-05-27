# --- START OF FILE app/game_state/entities/profession_definition_entity.py ---

import uuid
from dataclasses import field, KW_ONLY, asdict # <<< Import KW_ONLY and asdict
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from ..base import BaseEntity # Import the BaseEntity

# --- Enums (if needed) ---

# Use kw_only=True for the entire class if ALL fields defined here
# should be keyword-only (simplest approach)
# Or use the '_' marker before the first keyword-only field.
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
    # created_at and updated_at now come from BaseEntity

    # No need for __post_init__ just to set updated_at if created_at is handled okay
    # Keep __post_init__ for actual validation if needed
    # def __post_init__(self):
    #     if self.updated_at is None:
    #         self.updated_at = self.created_at

    # Inherits __repr__ from BaseEntity
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert all fields of this entity to a dictionary, including inherited fields.
        This is used for serialization to JSON or other formats.
        """
        # Start with the base entity fields
        result = super().to_dict()
        
        # Add all fields from this entity
        entity_dict = asdict(self)
        
        # Process UUIDs and datetimes for serialization
        for key, value in entity_dict.items():
            # Skip entity_id as it's already handled by the base class
            if key == "entity_id":
                continue
                
            # For UUIDs, convert to string
            if isinstance(value, uuid.UUID):
                result[key] = str(value)
            # For lists of UUIDs, convert each to string
            elif isinstance(value, list) and value and isinstance(value[0], uuid.UUID):
                result[key] = [str(item) for item in value]
            # For datetime, keep as is (it will be serialized to ISO format)
            elif isinstance(value, datetime):
                result[key] = value
            # For everything else, use as is
            else:
                result[key] = value
                
        return result

# --- END OF FILE app/game_state/entities/profession_definition_entity.py ---