"""
Repository for location types.
"""
from uuid import UUID
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.models.location_type import LocationType
from app.db.models.location_instance import LocationInstance as LocationEntityModel
from app.game_state.entities.geography.location import LocationTypeEntity
from app.game_state.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class LocationTypeRepository:
    """Repository for working with location types."""
    
    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db
    
    async def get_by_id(self, type_id: UUID) -> Optional[LocationTypeEntity]:
        """Get a location type by ID."""
        logger.info(f"LocationTypeRepository.get_by_id called with type_id={type_id}")
        repo = BaseRepository(self.db, LocationType, LocationTypeEntity)
        return await repo.find_by_id(type_id)
    
    async def get_by_code(self, code: str) -> Optional[LocationTypeEntity]:
        """Get a location type by code."""
        logger.info(f"LocationTypeRepository.get_by_code called with code={code}")
        repo = BaseRepository(self.db, LocationType, LocationTypeEntity)
        return await repo.get_by_field("code", code)
    
    async def get_all(self, theme: Optional[str] = None) -> List[LocationTypeEntity]:
        """Get all location types, optionally filtered by theme."""
        logger.info(f"LocationTypeRepository.get_all called with theme={theme}")
        repo = BaseRepository(self.db, LocationType, LocationTypeEntity)
        
        if theme:
            stmt = select(LocationType).where(LocationType.theme == theme)
            result = await self.db.execute(stmt)
            rows = result.scalars().all()
            
            return [await repo._convert_to_entity(row) for row in rows if row]
        else:
            return await repo.find_all(limit=1000)  # Adjust limit as needed
    
    async def create(self, location_type: LocationTypeEntity) -> LocationTypeEntity:
        """Create a new location type."""
        logger.info(f"LocationTypeRepository.create called with type={location_type.name}")
        repo = BaseRepository(self.db, LocationType, LocationTypeEntity)
        return await repo.save(location_type)
    
    async def update(self, location_type: LocationTypeEntity) -> LocationTypeEntity:
        """Update an existing location type."""
        logger.info(f"LocationTypeRepository.update called with type={location_type.name}")
        repo = BaseRepository(self.db, LocationType, LocationTypeEntity)
        return await repo.save(location_type)
    
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
            return False  # Type is in use, can't delete
        
        # Delete the type
        repo = BaseRepository(self.db, LocationType, LocationTypeEntity)
        return await repo.delete(type_id)