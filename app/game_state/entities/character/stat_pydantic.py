from pydantic import Field, field_validator, ConfigDict
from uuid import UUID
from enum import Enum
from typing import Optional, Dict, Any

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

# Define stat-specific enum
class StatCategory(Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    DERIVED = "DERIVED"
    RESISTANCE = "RESISTANCE"
    COMBAT = "COMBAT"
    CRAFTING = "CRAFTING"

class StatEntityPydantic(BaseEntityPydantic):
    """
    Domain Entity representing a character or item stat.
    Inherits entity_id and name from BaseEntityPydantic.
    """
    # Stat values
    value: float = 0.0
    min_value: float = 0.0
    max_value: float = 100.0
    category: StatCategory = StatCategory.PRIMARY
    
    # Description and metadata
    description: Optional[str] = None
    modifier: Optional[float] = None
    is_active: bool = True
    
    # Additional metadata
    # tags is now inherited from BaseEntityPydantic
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Relationships
    owner_character_id: Optional[UUID] = None
    
    # Value validation logic from __post_init__
    @field_validator('value')
    @classmethod
    def validate_value(cls, v, values):
        """Ensure value is within min_value and max_value"""
        if 'min_value' in values.data and v < values.data['min_value']:
            return values.data['min_value']
        elif 'max_value' in values.data and v > values.data['max_value']:
            return values.data['max_value']
        return v
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Strength",
                "value": 15.0,
                "min_value": 1.0,
                "max_value": 100.0,
                "category": "PRIMARY",
                "description": "Physical strength attribute",
                "is_active": True,
                "tags": ["attribute", "physical"]
            }
        }
    )

# For backward compatibility
Stat = StatEntityPydantic