# --- START OF FILE app/game_state/entities/skill.py ---

import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from .base import BaseEntity
from app.game_state.enums.skill import SkillStatus

@dataclass
class SkillEntity(BaseEntity):
    """
    Domain Entity representing a character skill.
    Inherits entity_id and name from BaseEntity.
    """
    # Skill attributes
    level: int = 0
    max_level: int = 100
    status: SkillStatus = SkillStatus.LOCKED
    
    # Description and metadata
    description: Optional[str] = None
    category: Optional[str] = None
    icon_path: Optional[str] = None
    
    # Timestamps are now handled by BaseEntity
    
    # Additional metadata
    # tags is now inherited from BaseEntity
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Relationships
    prerequisite_skill_ids: List[uuid.UUID] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize fields as needed."""
        # BaseEntity now handles timestamp initialization


# --- END OF FILE app/game_state/entities/skill.py ---