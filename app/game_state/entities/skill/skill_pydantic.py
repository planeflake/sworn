from pydantic import Field, ConfigDict
from uuid import UUID
from typing import Optional, List, Dict, Any

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic
from app.game_state.enums.skill import SkillStatus

class SkillEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing a character skill.
    Inherits entity_id and name from BaseEntityPydantic.
    """
    # Skill attributes
    level: int = 0
    max_level: int = 100
    status: SkillStatus = SkillStatus.LOCKED
    
    # Description and metadata
    description: Optional[str] = None
    category: Optional[str] = None
    icon_path: Optional[str] = None
    
    # Additional metadata
    # tags is now inherited from BaseEntityPydantic
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Relationships
    prerequisite_skill_ids: List[UUID] = Field(default_factory=list)
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Swordsmanship",
                "level": 5,
                "max_level": 100,
                "status": "ACTIVE",
                "description": "Proficiency with swords and other bladed weapons",
                "category": "Combat",
                "icon_path": "/assets/icons/sword.png",
                "tags": ["combat", "melee", "weapon"],
                "prerequisite_skill_ids": ["550e8400-e29b-41d4-a716-446655440000"]
            }
        }
    )

# For backward compatibility
Skill = SkillEntityPydantic