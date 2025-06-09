from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID

class ActionRequirementSchema(BaseModel):
    """Schema for action requirements."""
    skill_id: Optional[UUID] = None
    skill_level: int = 0
    required_tool_tier_id: Optional[UUID] = None
    required_item_ids: List[UUID] = Field(default_factory=list)
    required_location_type_ids: List[UUID] = Field(default_factory=list)
    stamina_cost: int = 0


class ActionRewardSchema(BaseModel):
    """Schema for action rewards."""
    resource_id: Optional[UUID] = None
    item_id: Optional[UUID] = None
    quantity_min: int = 1
    quantity_max: int = 1
    drop_chance: float = 1.0
    experience_points: int = 0


class ActionTemplateCreateSchema(BaseModel):
    """Schema for creating action templates."""
    name: str = Field(..., min_length=1, max_length=255)
    category_id: UUID
    description: str = ""
    action_verb: str = "perform"
    requirements: ActionRequirementSchema = Field(default_factory=ActionRequirementSchema)
    possible_rewards: List[ActionRewardSchema] = Field(default_factory=list)
    base_duration_seconds: int = Field(60, ge=1)
    difficulty_level: int = Field(1, ge=1)
    max_skill_level: Optional[int] = Field(None, ge=1)
    icon: Optional[str] = None
    flavor_text: Optional[str] = None
    display_order: int = 0
    is_repeatable: bool = True
    prerequisite_action_ids: List[UUID] = Field(default_factory=list)
    unlock_world_day: int = Field(0, ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Gather Softwood",
                "category_id": "123e4567-e89b-12d3-a456-426614174000",
                "description": "Collect basic wood from young trees",
                "action_verb": "gather",
                "requirements": {
                    "skill_id": "987fcdeb-51a2-43d1-b456-426614174000",
                    "skill_level": 1,
                    "required_tool_tier_id": "456e7890-e89b-12d3-a456-426614174001",
                    "required_location_type_ids": ["456e7890-e89b-12d3-a456-426614174000"]
                },
                "possible_rewards": [
                    {
                        "resource_id": "789abcde-e89b-12d3-a456-426614174000",
                        "quantity_min": 1,
                        "quantity_max": 3,
                        "drop_chance": 1.0,
                        "experience_points": 10
                    }
                ],
                "base_duration_seconds": 30,
                "difficulty_level": 1
            }
        }
    )


class ActionTemplateUpdateSchema(BaseModel):
    """Schema for updating action templates."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    action_verb: Optional[str] = None
    requirements: Optional[ActionRequirementSchema] = None
    possible_rewards: Optional[List[ActionRewardSchema]] = None
    base_duration_seconds: Optional[int] = Field(None, ge=1)
    difficulty_level: Optional[int] = Field(None, ge=1)
    max_skill_level: Optional[int] = Field(None, ge=1)
    icon: Optional[str] = None
    flavor_text: Optional[str] = None
    display_order: Optional[int] = None
    is_repeatable: Optional[bool] = None
    is_active: Optional[bool] = None
    prerequisite_action_ids: Optional[List[UUID]] = None
    unlock_world_day: Optional[int] = Field(None, ge=0)


class ActionTemplateResponseSchema(BaseModel):
    """Schema for action template responses."""
    entity_id: UUID
    name: str
    category_id: UUID
    description: str
    action_verb: str
    requirements: ActionRequirementSchema
    possible_rewards: List[ActionRewardSchema]
    base_duration_seconds: int
    difficulty_level: int
    max_skill_level: Optional[int]
    icon: Optional[str]
    flavor_text: Optional[str]
    display_order: int
    is_repeatable: bool
    is_active: bool
    prerequisite_action_ids: List[UUID]
    unlock_world_day: int


class ActionCategoryCreateSchema(BaseModel):
    """Schema for creating action categories."""
    name: str = Field(..., min_length=1, max_length=255)
    parent_category_id: Optional[UUID] = None
    description: str = ""
    icon: Optional[str] = None
    display_order: int = 0

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Gathering",
                "description": "Actions related to resource collection",
                "icon": "🌳",
                "display_order": 1
            }
        }
    )


class ActionCategoryUpdateSchema(BaseModel):
    """Schema for updating action categories."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    parent_category_id: Optional[UUID] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class ActionCategoryResponseSchema(BaseModel):
    """Schema for action category responses."""
    entity_id: UUID
    name: str
    parent_category_id: Optional[UUID]
    description: str
    icon: Optional[str]
    display_order: int
    is_active: bool
    child_categories: List["ActionCategoryResponseSchema"] = Field(default_factory=list)


class AvailableActionsQuerySchema(BaseModel):
    """Schema for querying available actions."""
    character_id: UUID
    location_type_id: UUID
    tool_tier_id: Optional[UUID] = None


# Fix forward reference
ActionCategoryResponseSchema.model_rebuild()