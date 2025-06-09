# --- START OF FILE app/game_state/repositories/skill_definition_repository.py ---

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional, Dict, Any
import logging

from app.db.models.skill_definition import SkillDefinition # SQLAlchemy Model
from app.game_state.entities.skill.skill_definition_pydantic import SkillDefinitionEntityPydantic # Domain Entity
from app.game_state.repositories.base_repository import BaseRepository

class SkillDefinitionRepository(BaseRepository[SkillDefinitionEntityPydantic, SkillDefinition, UUID]):
    """
    Repository for SkillDefinition data operations.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model_cls=SkillDefinition, entity_cls=SkillDefinitionEntityPydantic)
        logging.info("SkillDefinitionRepository initialized.")

    # Example: Find skills relevant to specific themes
    async def find_by_themes(self, theme_names: List[str]) -> List[SkillDefinitionEntityPydantic]:
         """Finds skill definitions relevant to any of the given theme names."""
         if not theme_names:
             return []
         logging.debug(f"Finding skill definitions for themes: {theme_names}")
         # Use array overlap operator '&&' for PostgreSQL ARRAY[String]
         stmt = select(self.model_cls).where(self.model_cls.themes.overlap(theme_names))
         result = await self.db.execute(stmt)
         db_objs = result.scalars().all()
         entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
         return [entity for entity in entities if entity is not None]


# --- END OF FILE app/game_state/repositories/skill_definition_repository.py ---