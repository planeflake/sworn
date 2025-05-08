# --- START OF FILE app/game_state/repositories/profession_repository.py ---

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

from app.db.models.profession_definition import ProfessionDefinition # SQLAlchemy Model
from app.game_state.entities.profession_definition_entity import ProfessionDefinitionEntity # Domain Entity
from app.game_state.repositories.base_repository import BaseRepository
import logging

class ProfessionRepository(BaseRepository[ProfessionDefinitionEntity, ProfessionDefinition, UUID]):
    """
    Repository for ProfessionDefinition data operations.
    Inherits standard CRUD and conversion logic from BaseRepository.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model_cls=ProfessionDefinition, entity_cls=ProfessionDefinitionEntity)
        logging.info("ProfessionRepository initialized.")

    # Add custom query methods if needed, e.g.:
    async def find_by_name(self, name: str) -> Optional[ProfessionDefinitionEntity]:
        """Finds a profession definition by its unique name."""
        logging.debug(f"Finding profession definition by name: {name}")
        stmt = select(self.model_cls).where(self.model_cls.name == name)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return await self._convert_to_entity(db_obj)
        return None

    async def find_by_theme(self, theme_id: UUID, skip: int = 0, limit: int = 100) -> List[ProfessionDefinitionEntity]:
         """Finds profession definitions available for a specific theme."""
         logging.debug(f"Finding professions for theme_id: {theme_id} (skip={skip}, limit={limit})")
         # This query uses the ARRAY contains operator (@>) for PostgreSQL
         # Adapt if using a different storage method (JSON, association table)
         stmt = (
             select(self.model_cls)
             .where(self.model_cls.available_theme_ids.contains([theme_id]))
             .offset(skip)
             .limit(limit)
         )
         result = await self.db.execute(stmt)
         db_objs = result.scalars().all()
         entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
         return [entity for entity in entities if entity is not None]

# --- END OF FILE app/game_state/repositories/profession_repository.py ---