# --- START OF FILE app/game_state/entities/skill.py ---

import uuid
import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from .base import BaseEntity

# Define skill-specific enum
class SkillStatus(enum.Enum):
    LOCKED = "LOCKED"
    AVAILABLE = "AVAILABLE"
    LEARNING = "LEARNING"
    MASTERED = "MASTERED"

@dataclass
class SkillEntity(BaseEntity):
    """
    Domain Entity representing a character skill.
    Inherits entity_id and name from BaseEntity.
    """
    # Skill attributes
    level: int = 0
    max_level: int = 100
    experience: int = 0
    experience_to_next_level: int = 100
    status: SkillStatus = SkillStatus.LOCKED
    
    # Description and metadata
    description: Optional[str] = None
    category: Optional[str] = None
    icon_path: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    unlocked_at: Optional[datetime] = None
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Relationships
    prerequisite_skill_ids: List[uuid.UUID] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize fields as needed."""
        if self.updated_at is None:
            self.updated_at = self.created_at
            
        if self.status != SkillStatus.LOCKED and self.unlocked_at is None:
            self.unlocked_at = self.created_at

# --- END OF FILE app/game_state/entities/skill.py ---