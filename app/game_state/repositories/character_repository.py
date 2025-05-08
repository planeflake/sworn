from app.game_state.models.character import Character as CharacterModel
from app.game_state.entities.character import Character as CharacterEntity
from app.game_state.repositories.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any, Type
from uuid import UUID

class SettlementRepository(BaseRepository[CharacterEntity, CharacterModel, UUID]):
    """
    Repository specifically for Settlement entities. Needs entity_cls for conversion.
    """
    def __init__(self, db: AsyncSession):
        # Pass both the DB model class AND the domain entity class to the base repository
        super().__init__(db=db, model_cls=CharacterModel, entity_cls=CharacterEntity) # Pass entity_cls