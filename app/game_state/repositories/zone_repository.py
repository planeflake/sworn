from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List
import logging

from app.game_state.repositories.base_repository import BaseRepository
from app.game_state.entities.zone import Zone as ZoneEntity
from app.db.models.zone import Zone as ZoneModel  # This is the SQLAlchemy model for the DB

class ZoneRepository(BaseRepository[ZoneEntity, ZoneModel, UUID]):
    """
    Repository for working with Zone entities.
    Maps between domain entity (ZoneEntity) and database model (ZoneModel).
    """
    def __init__(self, db: AsyncSession):
        """Initialize the ZoneRepository with a database session."""
        self.db = db
        super().__init__(db=db, model_cls=ZoneModel, entity_cls=ZoneEntity)
        logging.info(f"ZoneRepository initialized with model {ZoneModel.__name__} and entity {ZoneEntity.__name__}")
    
    async def find_by_world_id(self, world_id: UUID) -> List[ZoneEntity]:
        """Find all zones in a specific world."""
        logging.debug(f"[ZoneRepository] Finding zones for world: {world_id}")
        try:
            stmt = select(self.model_cls).where(self.model_cls.world_id == world_id)
            result = await self.db.execute(stmt)
            db_objs = result.scalars().all()
            
            # Convert each DB model to a domain entity
            entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
            entities = [entity for entity in entities if entity is not None]  # Filter out None values
            
            logging.debug(f"[ZoneRepository] Found {len(entities)} zones for world ID {world_id}")
            return entities
        except Exception as e:
            logging.error(f"[ZoneRepository] Error finding zones for world {world_id}: {e}", exc_info=True)
            return []
    
    async def find_by_biome_id(self, biome_id: UUID) -> List[ZoneEntity]:
        """Find all zones associated with a specific biome."""
        logging.debug(f"[ZoneRepository] Finding zones for biome: {biome_id}")
        try:
            stmt = select(self.model_cls).where(self.model_cls.biome_id == biome_id)
            result = await self.db.execute(stmt)
            db_objs = result.scalars().all()
            
            entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
            entities = [entity for entity in entities if entity is not None]
            
            logging.debug(f"[ZoneRepository] Found {len(entities)} zones for biome ID {biome_id}")
            return entities
        except Exception as e:
            logging.error(f"[ZoneRepository] Error finding zones for biome {biome_id}: {e}", exc_info=True)
            return []