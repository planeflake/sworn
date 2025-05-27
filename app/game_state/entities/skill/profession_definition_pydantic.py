from pydantic import Field, ConfigDict
from uuid import UUID
from typing import Optional, List, Dict, Any

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class ProfessionDefinitionEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing a Profession Definition/Blueprint.
    Inherits 'entity_id' (UUID) and 'name' (str) from BaseEntityPydantic.
    """
    display_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    skill_requirements: List[Dict[str, Any]] = Field(default_factory=list)
    available_theme_ids: List[UUID] = Field(default_factory=list)
    valid_unlock_methods: List[str] = Field(default_factory=list)
    unlock_condition_details: List[Dict[str, Any]] = Field(default_factory=list)
    python_class_override: Optional[str] = None
    archetype_handler: Optional[str] = None
    configuration_data: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert all fields of this entity to a dictionary, including inherited fields.
        This is used for serialization to JSON or other formats.
        """
        # Start with the base entity fields
        result = super().to_dict()
        
        # Process fields that need special handling for serialization
        profession_data = {
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "skill_requirements": self.skill_requirements,
            "available_theme_ids": [str(theme_id) for theme_id in self.available_theme_ids],
            "valid_unlock_methods": self.valid_unlock_methods,
            "unlock_condition_details": self.unlock_condition_details,
            "python_class_override": self.python_class_override,
            "archetype_handler": self.archetype_handler,
            "configuration_data": self.configuration_data,
        }
        
        result.update(profession_data)
        return result
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "blacksmith",
                "display_name": "Blacksmith",
                "description": "Crafts weapons and armor from metal",
                "category": "crafting",
                "skill_requirements": [
                    {"skill_id": "550e8400-e29b-41d4-a716-446655440000", "level": 5}
                ],
                "available_theme_ids": ["550e8400-e29b-41d4-a716-446655440001"],
                "valid_unlock_methods": ["quest", "trainer"],
                "configuration_data": {
                    "primary_attribute": "strength",
                    "tool_requirement": "hammer"
                }
            }
        }
    )

# For backward compatibility
ProfessionDefinition = ProfessionDefinitionEntityPydantic