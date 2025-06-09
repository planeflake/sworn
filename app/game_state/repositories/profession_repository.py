# --- START OF FILE app/game_state/repositories/profession_repository.py ---

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.models.profession_definition import ProfessionDefinition # SQLAlchemy Model
from app.game_state.entities.skill.profession_definition_pydantic import ProfessionDefinitionEntityPydantic # Domain Entity
from app.game_state.repositories.base_repository import BaseRepository
import logging

class ProfessionRepository(BaseRepository[ProfessionDefinitionEntityPydantic, ProfessionDefinition, UUID]):
    """
    Repository for ProfessionDefinition data operations.
    Inherits standard CRUD and conversion logic from BaseRepository.
    """
    def __init__(self, db: AsyncSession):
        actual_model_cls = ProfessionDefinition # Or however you pass it if not hardcoded
        logging.info(
            f"ProfessionRepository initializing. Expected model: ProfessionDefinition, "
            f"Actual model passed to BaseRepository: {actual_model_cls.__name__}, "
            f"Table name: {actual_model_cls.__tablename__}"
        )
        super().__init__(db=db, model_cls=ProfessionDefinition, entity_cls=ProfessionDefinitionEntityPydantic)
        logging.info("ProfessionRepository initialized.")


# --- END OF FILE app/game_state/repositories/profession_repository.py ---