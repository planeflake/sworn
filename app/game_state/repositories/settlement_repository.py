# START OF FILE settlement_repository.py

from .base_repository import BaseRepository
# Use aliases for clarity
from app.game_state.entities.settlement import Settlement as SettlementEntity # Domain Entity (dataclass)
from app.db.models.settlement import Settlement as SettlementModel # DB Model (SQLAlchemy)
from app.db.async_session import AsyncSession
from typing import List, Optional, Dict, Any, Type
from sqlalchemy.future import select
from uuid import UUID
import dataclasses # Import dataclasses

class SettlementRepository(BaseRepository[SettlementEntity, SettlementModel, UUID]):
    """
    Repository specifically for Settlement entities. Needs entity_cls for conversion.
    """
    def __init__(self, db: AsyncSession):
        # Pass both the DB model class AND the domain entity class to the base repository
        super().__init__(db=db, model_cls=SettlementModel, entity_cls=SettlementEntity) # Pass entity_cls

    async def find_by_world(self, world_id: UUID) -> List[SettlementEntity]:
        stmt = select(self.model_cls).where(self.model_cls.world_id == world_id)
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        # Ensure _convert_to_entity in BaseRepository uses self.entity_cls
        return [await self._convert_to_entity(db_obj) for db_obj in db_objs]

# END OF FILE settlement_repository.py