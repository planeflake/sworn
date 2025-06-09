from pydantic import Field, BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic


class ActionRequirement(BaseModel):
    """Represents a requirement for performing an action."""
    skill_id: Optional[UUID] = None
    skill_level: int = 0
    required_tool_tier_id: Optional[UUID] = None  # Specific tool tier instance
    required_tool_tier_level: Optional[int] = None  # Minimum tool tier level (1-6)
    required_item_ids: List[UUID] = Field(default_factory=list)
    required_location_type_ids: List[UUID] = Field(default_factory=list)
    stamina_cost: int = 0
    
    
class ActionReward(BaseModel):
    """Represents potential rewards from an action."""
    resource_id: Optional[UUID] = None
    item_id: Optional[UUID] = None
    quantity_min: int = 1
    quantity_max: int = 1
    drop_chance: float = 1.0  # 0.0 to 1.0
    experience_points: int = 0


class ActionTemplatePydantic(BaseEntityPydantic):
    """
    Defines a template for actions that can be performed at locations.
    Links skills, items, and locations via UUIDs for flexible action discovery.
    """
    category_id: UUID
    description: str = ""
    action_verb: str = "perform"  # "gather", "craft", "build", etc.
    
    # Requirements to perform this action
    requirements: ActionRequirement = Field(default_factory=ActionRequirement)
    
    # Potential rewards from this action
    possible_rewards: List[ActionReward] = Field(default_factory=list)
    
    # Timing and progression
    base_duration_seconds: int = 60
    difficulty_level: int = 1
    max_skill_level: Optional[int] = None  # Level cap for this action
    
    # UI and display
    icon: Optional[str] = None
    flavor_text: Optional[str] = None
    display_order: int = 0
    is_repeatable: bool = True
    is_active: bool = True
    
    # Unlock conditions
    prerequisite_action_ids: List[UUID] = Field(default_factory=list)
    unlock_world_day: int = 0  # Game day when this becomes available
    
    def get_effective_duration(self, character_skill_level: int, tool_effectiveness_multiplier: float = 1.0) -> int:
        """Calculate actual duration based on skill level and tool quality."""
        duration = self.base_duration_seconds
        
        # Skill level reduces duration
        if character_skill_level > self.requirements.skill_level:
            skill_bonus = (character_skill_level - self.requirements.skill_level) * 0.05
            duration = int(duration * (1 - min(skill_bonus, 0.5)))  # Max 50% reduction
        
        # Tool tier provides efficiency bonus
        duration = int(duration / tool_effectiveness_multiplier)
        
        return max(duration, 5)  # Minimum 5 seconds
    
    def can_perform(
        self, 
        character_skill_level: int, 
        available_tool_tier_level: Optional[int] = None,
        required_tool_tier_level: Optional[int] = None
    ) -> bool:
        """Check if character can perform this action."""
        # Check skill level
        if character_skill_level < self.requirements.skill_level:
            return False
            
        # Check tool tier requirement
        if required_tool_tier_level and available_tool_tier_level:
            if available_tool_tier_level < required_tool_tier_level:
                return False
                
        return True