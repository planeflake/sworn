# --- START OF FILE app/game_state/entities/skill_definition_entity.py ---

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from .base import BaseEntity # Inherit from BaseEntity

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
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = self.created_at

    # Inherits __repr__ from BaseEntity

# --- END OF FILE app/game_state/entities/skill_definition_entity.py ---