# --- START OF FILE app/game_state/entities/skill_definition_entity.py ---

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from ..base import BaseEntity # Inherit from BaseEntity

@dataclass
class SkillDefinitionEntity(BaseEntity):
    """
    Domain Entity representing a Skill Definition.
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntity.
    'name' here represents the user-facing name.
    """
    # entity_id, name inherited

    # Optional: Add a unique key if needed, distinct from display name
    # skill_key: str

    description: Optional[str] = None
    max_level: int = 100
    themes: List[str] = field(default_factory=list) # List of theme names/IDs
    metadata: Dict[str, Any] = field(default_factory=dict) # Using metadata in entity but maps to _metadata in DB model

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # Ensure created_at is set
        if not hasattr(self, 'created_at') or self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
            
        # Set updated_at to created_at if not already set
        if not hasattr(self, 'updated_at') or self.updated_at is None:
            self.updated_at = self.created_at

    # Inherits __repr__ from BaseEntity

# --- END OF FILE app/game_state/entities/skill_definition_entity.py ---