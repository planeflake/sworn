# --- START OF FILE app/game_state/repositories/biome_repository.py ---
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional
import logging

from app.db.models.biome import Biome as BiomeModel # DB Model
from app.game_state.entities.geography.biome_pydantic import BiomeEntityPydantic # Domain Entity
from app.game_state.repositories.base_repository import BaseRepository

class BiomeRepository(BaseRepository[BiomeEntityPydantic, BiomeModel, UUID]):
    def __init__(self, db: AsyncSession):
        """Initializes the BiomeRepository."""
        # Pass the DB session, SQLAlchemy model, and Domain entity
        super().__init__(db=db, model_cls=BiomeModel, entity_cls=BiomeEntityPydantic)
        logging.info(f"BiomeRepository initialized with model {BiomeModel.__name__} and entity {BiomeEntityPydantic.__name__}")


    async def find_by_movement_modifier(self, min_modifier: float, max_modifier: float) -> List[BiomeEntityPydantic]:
        """Finds biomes within a given movement modifier range."""
        logging.debug(f"[BiomeRepository] Finding biomes with movement modifier between {min_modifier} and {max_modifier}")
        stmt = select(self.model_cls).where(
            self.model_cls.base_movement_modifier >= min_modifier,
            self.model_cls.base_movement_modifier <= max_modifier
        ).order_by(self.model_cls.base_movement_modifier.desc())
        
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
        return [entity for entity in entities if entity is not None]

    async def find_by_danger_level(self, danger_level: int) -> List[BiomeEntityPydantic]:
        """Finds biomes with the specified danger level."""
        logging.debug(f"[BiomeRepository] Finding biomes with danger level: {danger_level}")
        stmt = select(self.model_cls).where(self.model_cls.danger_level_base == danger_level)
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
        return [entity for entity in entities if entity is not None]

# --- END OF FILE app/game_state/repositories/biome_repository.py ---