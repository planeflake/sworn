import uuid
from typing import Optional, List
from datetime import datetime

from app.game_state.entities.action.action_template_pydantic import (
    ActionTemplatePydantic, 
    ActionRequirement, 
    ActionReward
)
from .base_manager import BaseManager


class ActionTemplateManager(BaseManager[ActionTemplatePydantic]):
    """Manager for action template business logic and creation."""
    
    @staticmethod
    def create_template(
        name: str,
        category_id: uuid.UUID,
        description: str = "",
        action_verb: str = "perform",
        requirements: Optional[ActionRequirement] = None,
        possible_rewards: Optional[List[ActionReward]] = None,
        base_duration_seconds: int = 60,
        difficulty_level: int = 1,
        entity_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> ActionTemplatePydantic:
        """Create a new action template."""
        create_params = {
            "name": name,
            "category_id": category_id,
            "description": description,
            "action_verb": action_verb,
            "requirements": requirements or ActionRequirement(),
            "possible_rewards": possible_rewards or [],
            "base_duration_seconds": base_duration_seconds,
            "difficulty_level": difficulty_level,
            "is_active": True,
            "is_repeatable": True,
            **kwargs
        }
        
        if entity_id:
            create_params["entity_id"] = entity_id
            
        return ActionTemplateManager.create(ActionTemplatePydantic, **create_params)
    
    @staticmethod
    def create_gathering_template(
        name: str,
        category_id: uuid.UUID,
        skill_id: uuid.UUID,
        skill_level: int,
        required_tool_tier_level: Optional[int],
        location_type_ids: List[uuid.UUID],
        resource_rewards: List[tuple[uuid.UUID, int, int, float]],  # (resource_id, min_qty, max_qty, chance)
        base_duration: int = 60,
        **kwargs
    ) -> ActionTemplatePydantic:
        """Create a gathering action template (simplified factory method)."""
        requirements = ActionRequirement(
            skill_id=skill_id,
            skill_level=skill_level,
            required_tool_tier_level=required_tool_tier_level,
            required_location_type_ids=location_type_ids
        )
        
        rewards = []
        for resource_id, min_qty, max_qty, chance in resource_rewards:
            rewards.append(ActionReward(
                resource_id=resource_id,
                quantity_min=min_qty,
                quantity_max=max_qty,
                drop_chance=chance,
                experience_points=skill_level * 10  # Basic XP calculation
            ))
        
        return ActionTemplateManager.create_template(
            name=name,
            category_id=category_id,
            action_verb="gather",
            requirements=requirements,
            possible_rewards=rewards,
            base_duration_seconds=base_duration,
            difficulty_level=skill_level,
            **kwargs
        )
    
    @staticmethod
    def estimate_action_duration(
        template: ActionTemplatePydantic,
        character_skill_level: int,
        tool_tier_level: Optional[int] = None
    ) -> int:
        """Estimate how long this action will take for a specific character."""
        return template.get_effective_duration(character_skill_level, tool_tier_level)