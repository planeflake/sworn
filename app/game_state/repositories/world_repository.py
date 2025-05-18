# app/game_state/repositories/world_repository.py
import os
import redis.asyncio as redis
from app.db.models.world import World as WorldModel
from app.game_state.entities.world import WorldEntity
from app.game_state.repositories.base_repository import BaseRepository
import logging
from typing import Optional, Dict, Any
from app.db.async_session import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime

# Get Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Redis key (adjust as needed)
WORLD_KEY_PREFIX = "world:state:"

# Create Async Redis client pool (recommended)
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD,
    decode_responses=True
)

class WorldRepository(BaseRepository[WorldEntity, WorldModel, UUID]):
    def __init__(self, db: AsyncSession, model_cls=WorldModel, entity_cls=WorldEntity):
        """
        Initializes the WorldRepository with a database session and model class.
        
        Args:
            db: The asynchronous SQLAlchemy session.
            model_cls: The SQLAlchemy model class
            entity_cls: The domain entity class 
        """
        super().__init__(db=db, model_cls=model_cls, entity_cls=entity_cls)
        logging.info(f"WorldRepository initialized with model {model_cls.__name__} and entity {entity_cls.__name__}")

    @staticmethod
    def _serialize_for_json(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert UUID and datetime objects to strings for JSON serialization"""
        result = {}
        for key, value in data.items():
            if isinstance(value, UUID):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
        
    async def find_by_name(self, name: str) -> Optional[WorldEntity]:
        """Finds a world by its name."""
        logging.debug(f"[WorldRepository] Finding world by name: {name}")
        stmt = select(self.model_cls).where(self.model_cls.name == name)
        result = await self.db.execute(stmt)
        db_obj = result.scalars().first()
        if db_obj:
            logging.debug(f"[WorldRepository] Found world by name: {name}, ID: {db_obj.id}")
            return await self._convert_to_entity(db_obj)
        else:
            logging.debug(f"[WorldRepository] World not found by name: {name}")
            return None