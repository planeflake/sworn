# --- START OF FILE app/game_state/repositories/building_instance_repository.py ---

import logging
from uuid import UUID
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # For eager loading relationships

from app.db.models.building_instance import BuildingInstanceDB
from app.game_state.entities.building_instance import BuildingInstanceEntity
from app.game_state.repositories.base_repository import BaseRepository

class BuildingInstanceRepository(BaseRepository[BuildingInstanceEntity, BuildingInstanceDB, UUID]):
    """
    Repository for BuildingInstanceDB data operations.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model_cls=BuildingInstanceDB, entity_cls=BuildingInstanceEntity)
        logging.info(
            f"BuildingInstanceRepository initialized with model: {self.model_cls.__name__} "
            f"and entity: {self.entity_cls.__name__}"
        )

    async def find_by_settlement_id(self, settlement_id: UUID, skip: int = 0, limit: int = 100) -> List[BuildingInstanceEntity]:
        """Finds all building instances within a specific settlement."""
        logging.debug(f"Finding building instances for settlement_id: {settlement_id} (skip={skip}, limit={limit})")
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.settlement_id == settlement_id)
            .options(selectinload(self.model_cls.blueprint)) # Example of eager loading blueprint info
            .offset(skip)
            .limit(limit)
            .order_by(self.model_cls.name) # Optional: order by name or created_at
        )
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
        return [entity for entity in entities if entity is not None]

    async def find_by_blueprint_id(self, blueprint_id: UUID, skip: int = 0, limit: int = 100) -> List[BuildingInstanceEntity]:
        """Finds all building instances based on a specific blueprint."""
        logging.debug(f"Finding building instances for blueprint_id: {blueprint_id} (skip={skip}, limit={limit})")
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.building_blueprint_id == blueprint_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
        return [entity for entity in entities if entity is not None]

    # You can add more specific query methods as needed, e.g.,
    # find_under_construction_in_settlement, find_damaged_buildings, etc.

    async def get_instance_with_details(self, instance_id: UUID) -> Optional[BuildingInstanceEntity]:
        """Gets a single building instance with eagerly loaded related data."""
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.id == instance_id)
            .options(
                selectinload(self.model_cls.blueprint), # Eager load blueprint
                selectinload(self.model_cls.settlement),  # Eager load settlement
                selectinload(self.model_cls.residents),   # Eager load residents
                selectinload(self.model_cls.workers)      # Eager load workers
            )
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return await self._convert_to_entity(db_obj)
        return None

# --- END OF FILE app/game_state/repositories/building_instance_repository.py ---