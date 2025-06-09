
import logging
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.managers.skill_definition_manager import SkillDefinitionManager
from app.game_state.repositories.skill_definition_repository import SkillDefinitionRepository
from app.api.schemas.skill import SkillCreate, SkillRead
from app.game_state.entities.skill.skill_definition_pydantic import SkillDefinitionEntityPydantic

class SkillService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.manager = SkillDefinitionManager
        self.repository = SkillDefinitionRepository(db=db)

    async def get_skill(self, skill_id: UUID) -> Optional[SkillRead]:
        """Get a skill by ID and return as API schema."""
        logging.debug(f"[SkillService] Getting skill by ID: {skill_id}")
        
        skill_entity = await self.repository.find_by_id(skill_id)
        if skill_entity:
            return SkillRead.model_validate(skill_entity.to_dict())
        return None

    async def add_skill(self, skill_data: SkillCreate) -> SkillRead:
        """Create a new skill and return as API schema."""
        logging.info(f"[SkillService] Creating skill with name: {skill_data.name}")
        
        transient_skill: SkillDefinitionEntityPydantic = self.manager.create(
            name=skill_data.name,
            max_level=skill_data.max_level,
            description=skill_data.description,
            themes=skill_data.themes,
            metadata=skill_data.metadata
        )

        try:
            persistent_skill = await self.repository.save(transient_skill)
            logging.info(f"[SkillService] Skill '{persistent_skill.name}' created successfully")
            return SkillRead.model_validate(persistent_skill.to_dict())
        except Exception as e:
            logging.error(f"[SkillService] Error saving skill '{skill_data.name}': {e}", exc_info=True)
            raise ValueError(f"Failed to save skill: {e}") from e

    async def delete_skill(self, skill_id: UUID) -> bool:
        """Delete a skill by ID."""
        logging.info(f"[SkillService] Deleting skill with ID: {skill_id}")
        
        try:
            deleted = await self.repository.delete(skill_id)
            if deleted:
                logging.info(f"[SkillService] Skill {skill_id} deleted successfully")
            else:
                logging.warning(f"[SkillService] Skill {skill_id} not found for deletion")
            return deleted
        except Exception as e:
            logging.error(f"[SkillService] Error deleting skill {skill_id}: {e}", exc_info=True)
            return False

    async def rename_skill(self, skill_id: UUID, new_name: str) -> Optional[SkillRead]:
        """Rename a skill and return as API schema."""
        logging.info(f"[SkillService] Renaming skill {skill_id} to '{new_name}'")
        
        skill_entity = await self.repository.find_by_id(skill_id)
        if not skill_entity:
            logging.warning(f"[SkillService] Skill {skill_id} not found for renaming")
            return None
            
        skill_entity.name = new_name
        
        try:
            updated_skill = await self.repository.save(skill_entity)
            logging.info(f"[SkillService] Skill {skill_id} renamed successfully to '{new_name}'")
            return SkillRead.model_validate(updated_skill.to_dict())
        except Exception as e:
            logging.error(f"[SkillService] Error renaming skill {skill_id}: {e}", exc_info=True)
            raise ValueError(f"Failed to rename skill: {e}") from e