# --- START OF FILE app/game_state/repositories/skill_definition_repository.py ---

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional
import logging

from app.db.models.skill_definition import SkillDefinition # SQLAlchemy Model
from app.game_state.entities.skill_definition_entity import SkillDefinitionEntity # Domain Entity
from app.game_state.repositories.base_repository import BaseRepository

class SkillDefinitionRepository(BaseRepository[SkillDefinitionEntity, SkillDefinition, UUID]):
    """
    Repository for SkillDefinition data operations.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model_cls=SkillDefinition, entity_cls=SkillDefinitionEntity)
        logging.info("SkillDefinitionRepository initialized.")

    # Example custom query: Find by name (which should be unique)
    async def find_by_name(self, name: str) -> Optional[SkillDefinitionEntity]:
        """Finds a skill definition by its unique name."""
        logging.debug(f"Finding skill definition by name: {name}")
        stmt = select(self.model_cls).where(self.model_cls.name == name)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return await self._convert_to_entity(db_obj)
        return None

    # Example: Find skills relevant to specific themes
    async def find_by_themes(self, theme_names: List[str]) -> List[SkillDefinitionEntity]:
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