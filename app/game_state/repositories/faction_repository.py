# --- START OF FILE app/game_state/repositories/faction_repository.py ---

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.models.faction import Faction # SQLAlchemy Model
from app.game_state.entities.faction.faction_pydantic import FactionEntityPydantic # Domain Entity
from app.game_state.repositories.base_repository import BaseRepository
import logging

class FactionRepository(BaseRepository[FactionEntityPydantic, Faction, UUID]):
    """
    Repository for ProfessionDefinition data operations.
    Inherits standard CRUD and conversion logic from BaseRepository.
    """
    def __init__(self, db: AsyncSession):
        actual_model_cls = Faction # Or however you pass it if not hardcoded
        logging.info(
            f"FactionRepository initializing. Expected model: FactionDefinition, "
            f"Actual model passed to BaseRepository: {actual_model_cls.__name__}, "
            f"Table name: {actual_model_cls.__tablename__}"
        )
        super().__init__(db=db, model_cls=Faction, entity_cls=FactionEntityPydantic)
        logging.info("FactionRepository initialized.")


# --- END OF FILE app/game_state/repositories/profession_repository.py ---