# --- START OF FILE app/game_state/repositories/biome_repository.py ---
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional
import logging

from app.db.models.biome import Biome as BiomeModel # DB Model
from app.game_state.entities.biome import BiomeEntity # Domain Entity
from app.game_state.repositories.base_repository import BaseRepository

class BiomeRepository(BaseRepository[BiomeEntity, BiomeModel, UUID]):
    def __init__(self, db: AsyncSession):
        """Initializes the BiomeRepository."""
        # Pass the DB session, SQLAlchemy model, and Domain entity
        super().__init__(db=db, model_cls=BiomeModel, entity_cls=BiomeEntity)
        logging.info(f"BiomeRepository initialized with model {BiomeModel.__name__} and entity {BiomeEntity.__name__}")

    async def find_by_biome_id(self, biome_id: str) -> Optional[BiomeEntity]:
        """Finds a biome by its unique string identifier."""
        logging.debug(f"[BiomeRepository] Finding biome by biome_id: {biome_id}")
        stmt = select(self.model_cls).where(self.model_cls.biome_id == biome_id)
        result = await self.db.execute(stmt)
        db_obj = result.scalars().first()
        if db_obj:
            logging.debug(f"[BiomeRepository] Found biome by biome_id: {biome_id}, ID: {db_obj.id}")
            return await self._convert_to_entity(db_obj)
        else:
            logging.debug(f"[BiomeRepository] Biome not found by biome_id: {biome_id}")
            return None

    async def find_by_movement_modifier(self, min_modifier: float, max_modifier: float) -> List[BiomeEntity]:
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

    async def find_by_danger_level(self, danger_level: int) -> List[BiomeEntity]:
        """Finds biomes with the specified danger level."""
        logging.debug(f"[BiomeRepository] Finding biomes with danger level: {danger_level}")
        stmt = select(self.model_cls).where(self.model_cls.danger_level_base == danger_level)
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
        return [entity for entity in entities if entity is not None]

# --- END OF FILE app/game_state/repositories/biome_repository.py ---