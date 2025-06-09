"""
Repository for location types.
"""
from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.models.location_type import LocationType
from app.db.models.location_instance import LocationInstance as LocationEntityModel
from app.game_state.entities.geography.location_type_pydantic import LocationTypeEntityPydantic
from app.game_state.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class LocationTypeRepository(BaseRepository[LocationTypeEntityPydantic, LocationType, UUID]):
    """Repository for working with location types."""
    
    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        super().__init__(db=db, model_cls=LocationType, entity_cls=LocationTypeEntityPydantic)
    
    async def get_by_id(self, type_id: UUID) -> Optional[LocationTypeEntityPydantic]:
        """Get a location type by ID."""
        logger.info(f"LocationTypeRepository.get_by_id called with type_id={type_id}")
        return await self.find_by_id(type_id)
    
    async def get_by_code(self, code: str) -> Optional[LocationTypeEntityPydantic]:
        """Get a location type by code."""
        logger.info(f"LocationTypeRepository.get_by_code called with code={code}")
        stmt = select(LocationType).where(LocationType.code == code)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return await self._convert_to_entity(model) if model else None
    
    async def get_all(self, theme: Optional[str] = None) -> List[LocationTypeEntityPydantic]:
        """Get all location types, optionally filtered by theme."""
        logger.info(f"LocationTypeRepository.get_all called with theme={theme}")
        
        if theme:
            stmt = select(LocationType).where(LocationType.theme == theme)
            result = await self.db.execute(stmt)
            rows = result.scalars().all()
            
            entities = []
            for row in rows:
                entity = await self._convert_to_entity(row)
                if entity:
                    entities.append(entity)
            return entities
        else:
            return await self.find_all(limit=1000)  # Adjust limit as needed
    
    async def create(self, location_type: LocationTypeEntityPydantic) -> LocationTypeEntityPydantic:
        """Create a new location type."""
        logger.info(f"LocationTypeRepository.create called with type={location_type.name}")
        return await self.save(location_type)
    
    
    async def delete(self, type_id: UUID) -> bool:
        """Delete a location type if not in use."""
        logger.info(f"LocationTypeRepository.delete called with type_id={type_id}")
        # Check if any locations are using this type
        count_query = select(func.count()).select_from(LocationEntityModel).where(
            LocationEntityModel.location_type_id == type_id
        )
        count_result = await self.db.execute(count_query)
        count = count_result.scalar()
        
        if count > 0:
            return False
        
        # Delete the type
        return await self.delete(type_id)