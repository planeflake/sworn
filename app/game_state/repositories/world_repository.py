# app/game_state/repositories/world_repository.py
import json
import os
import redis.asyncio as redis
from app.db.models.world import World
from app.game_state.models.world import WorldEntity
from app.game_state.entities.world import World as WorldDomainEntity # Domain Entity (dataclass)
from app.game_state.repositories.base_repository import BaseRepository
import logging
from typing import List, Optional, Union, Dict, Any
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

class WorldRepository(BaseRepository[WorldDomainEntity, World, UUID]):
    def __init__(self, db: AsyncSession, model_cls: type = World, entity_cls: type = WorldDomainEntity):
        """
        Initializes the WorldRepository with a database session and model class.
        
        Args:
            db: The asynchronous SQLAlchemy session.
        """
        super().__init__(db=db, model_cls=World,entity_cls=WorldDomainEntity)

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
    