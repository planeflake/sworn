from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID

from app.db.models.action_template import ActionTemplate
from app.game_state.entities.action.action_template_pydantic import ActionTemplatePydantic
from .base_repository import BaseRepository


class ActionTemplateRepository(BaseRepository[ActionTemplatePydantic, ActionTemplate, UUID]):
    """Repository for managing action templates with location and skill filtering."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ActionTemplate, ActionTemplatePydantic)
    
    async def get_by_category(self, category_id: UUID) -> List[ActionTemplatePydantic]:
        """Get all action templates in a specific category."""
        stmt = select(ActionTemplate).where(
            and_(
                ActionTemplate.category_id == category_id,
                ActionTemplate.is_active == True
            )
        ).order_by(ActionTemplate.display_order, ActionTemplate.name)
        
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self.model_to_entity(model) for model in models]
    
    async def get_available_for_character(
        self, 
        location_type_id: UUID, 
        character_skills: dict[UUID, int],
        available_tool_tier_level: Optional[int] = None
    ) -> List[ActionTemplatePydantic]:
        """
        Get action templates available to a character based on their location,
        skills, and available tools.
        """
        # Get all active templates
        stmt = select(ActionTemplate).where(ActionTemplate.is_active == True)
        result = await self.db.execute(stmt)
        all_templates = [self.model_to_entity(model) for model in result.scalars().all()]
        
        available_templates = []
        for template in all_templates:
            # Check if character meets requirements
            if self._can_character_perform(template, location_type_id, character_skills, available_tool_tier_level):
                available_templates.append(template)
        
        return sorted(available_templates, key=lambda t: (t.display_order, t.name))
    
    async def get_templates_requiring_skill(self, skill_id: UUID) -> List[ActionTemplatePydantic]:
        """Get all action templates that require a specific skill."""
        stmt = select(ActionTemplate).where(ActionTemplate.is_active == True)
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        
        matching_templates = []
        for model in models:
            template = self.model_to_entity(model)
            if template.requirements.skill_id == skill_id:
                matching_templates.append(template)
        
        return matching_templates
    
    def _can_character_perform(
        self, 
        template: ActionTemplatePydantic, 
        location_type_id: UUID,
        character_skills: dict[UUID, int],
        available_tool_tier_level: Optional[int]
    ) -> bool:
        """Check if character can perform this action template."""
        req = template.requirements
        
        # Check location requirement
        if req.required_location_type_ids and location_type_id not in req.required_location_type_ids:
            return False
        
        # Check skill requirement
        if req.skill_id:
            character_skill_level = character_skills.get(req.skill_id, 0)
            if character_skill_level < req.skill_level:
                return False
        
        # Check tool tier requirement (this would need tool tier repository lookup in real implementation)
        # For now, simplified to just check tier levels
        if req.required_tool_tier_id and available_tool_tier_level:
            # In real implementation, would lookup required tool tier level from database
            # For now, assume we can get the level somehow
            # required_tier_level = await get_tool_tier_level(req.required_tool_tier_id)
            # if available_tool_tier_level < required_tier_level:
            #     return False
            pass
        
        return True