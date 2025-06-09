from pydantic import Field, ConfigDict
from typing import Optional, List, Dict, Any

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class SkillDefinitionEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing a Skill Definition.
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntityPydantic.
    'name' here represents the user-facing name.
    """
    # Optional: Add a unique key if needed, distinct from display name
    # skill_key: str
    
    description: Optional[str] = None
    max_level: int = 100
    themes: List[str] = Field(default_factory=list)  # List of theme names/IDs
    #metadata: Dict[str, Any] = Field(default_factory=dict)  # Using metadata in entity but maps to _metadata in DB model
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Swordsmanship",
                "description": "The art of wielding a sword in combat",
                "max_level": 100,
                "themes": ["fantasy", "medieval"],
                "metadata": {
                    "icon": "sword.png",
                    "category": "combat",
                    "attribute": "strength"
                }
            }
        }
    )

# For backward compatibility
SkillDefinition = SkillDefinitionEntityPydantic