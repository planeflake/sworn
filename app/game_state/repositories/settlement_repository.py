# START OF FILE settlement_repository.py

from .base_repository import BaseRepository
# Use aliases for clarity
from app.game_state.entities.settlement import SettlementEntity
from app.db.models.settlement import Settlement as SettlementModel
from app.db.async_session import AsyncSession
from typing import List, Optional
from sqlalchemy.future import select
from uuid import UUID
import logging

class SettlementRepository(BaseRepository[SettlementEntity, SettlementModel, UUID]):
    """
    Repository specifically for Settlement entities.
    """
    def __init__(self, db: AsyncSession):
        # Pass both the DB model class AND the domain entity class to the base repository
        super().__init__(db=db, model_cls=SettlementModel, entity_cls=SettlementEntity)
        logging.info(f"SettlementRepository initialized with model {SettlementModel.__name__} and entity {SettlementEntity.__name__}")

    async def find_by_world(self, world_id: UUID) -> List[SettlementEntity]:
        """Find all settlements in a specific world."""
        logging.debug(f"[SettlementRepository] Finding settlements for world: {world_id}")
        stmt = select(self.model_cls).where(self.model_cls.world_id == world_id)
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        settlements = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
        logging.debug(f"[SettlementRepository] Found {len(settlements)} settlements for world: {world_id}")
        return settlements

    async def rename(self, settlement_id: UUID, new_name: str) -> Optional[SettlementEntity]:
        """Rename a settlement."""
        logging.debug(f"[SettlementRepository] Renaming settlement {settlement_id} to '{new_name}'")
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.id == settlement_id)
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            db_obj.name = new_name
            await self.db.commit()
            updated_entity = await self._convert_to_entity(db_obj)
            logging.debug(f"[SettlementRepository] Successfully renamed settlement {settlement_id}")
            return updated_entity
        else:
            logging.warning(f"[SettlementRepository] Settlement {settlement_id} not found for rename")
            return None

    async def set_leader(self, settlement_id: UUID, leader_id: UUID) -> Optional[SettlementEntity]:
        """Set the leader of a settlement."""
        logging.debug(f"[SettlementRepository] Setting leader {leader_id} for settlement {settlement_id}")
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.id == settlement_id)
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            db_obj.leader_id = leader_id
            await self.db.commit()
            updated_entity = await self._convert_to_entity(db_obj)
            logging.debug(f"[SettlementRepository] Successfully set leader for settlement {settlement_id}")
            return updated_entity
        else:
            logging.warning(f"[SettlementRepository] Settlement {settlement_id} not found for setting leader")
            return None

    async def construct_building(self, settlement_id: UUID, building_id: str) -> Optional[SettlementEntity]:
        """Add a building to a settlement."""
        # Implementation depends on how buildings are stored (JSONB array, relation table, etc.)
        # This is a placeholder implementation
        pass

    async def demolish_building(self, settlement_id: UUID, building_id: str) -> Optional[SettlementEntity]:
        """Remove a building from a settlement."""
        # Implementation depends on how buildings are stored (JSONB array, relation table, etc.)
        # This is a placeholder implementation
        pass

    async def add_resource(self, settlement_id: UUID, resource_id: str) -> Optional[SettlementEntity]:
        """Add a resource to a settlement."""
        # Implementation depends on how resources are stored (JSONB array, relation table, etc.)
        # This is a placeholder implementation
        pass

# END OF FILE settlement_repository.py