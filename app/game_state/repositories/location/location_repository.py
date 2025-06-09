"""
Repository for locations.
"""
from uuid import UUID
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.location_instance import LocationInstance as LocationEntityModel
from app.game_state.entities.geography.location_pydantic import LocationEntityPydantic
from app.game_state.repositories.location.location_type_repository import LocationTypeRepository
from app.game_state.repositories.base_repository import BaseRepository

class LocationRepository(BaseRepository[LocationEntityPydantic, LocationEntityModel, UUID]):
    """Repository for working with locations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        super().__init__(db=db, model_cls=LocationEntityModel, entity_cls=LocationEntityPydantic)
        self.type_repository = LocationTypeRepository(db)
    
    async def get_by_id(self, location_id: UUID) -> Optional[LocationEntityPydantic]:
        """Get a location by ID with its type."""
        # First get the location entity
        location = await self.find_by_id(location_id)
        
        if not location:
            return None
            
        # Load the location type
        location.location_type = await self.type_repository.get_by_id(
            location.location_type_id
        )
        
        return location
    
    async def get_by_type(self, type_id: UUID, limit: int = 100, offset: int = 0) -> List[LocationEntityPydantic]:
        """Get locations by type ID."""
        stmt = select(LocationEntityModel).where(
            LocationEntityModel.location_type_id == type_id
        ).limit(limit).offset(offset)
        
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        
        locations = []
        for row in rows:
            entity = await self._convert_to_entity(row)
            if entity:
                locations.append(entity)
        
        # Load the type entity once for all locations
        if locations:
            type_entity = await self.type_repository.get_by_id(type_id)
            for location in locations:
                location.location_type = type_entity
        
        return locations
    
    async def get_by_type_code(self, type_code: str, limit: int = 100, offset: int = 0) -> List[LocationEntityPydantic]:
        """Get locations by type code."""
        # First get the type ID
        type_entity = await self.type_repository.get_by_code(type_code)
        if not type_entity:
            return []
        
        return await self.get_by_type(type_entity.entity_id, limit, offset)
    
    async def get_children(
        self,
        parent_id: UUID,
        child_type_id: Optional[UUID] = None
    ) -> List[LocationEntityPydantic]:
        """Get child locations of a parent."""
        stmt = select(LocationEntityModel).where(
            LocationEntityModel.parent_id == parent_id
        )
        
        if child_type_id:
            stmt = stmt.where(
                LocationEntityModel.location_type_id == child_type_id
            )
        
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        
        locations = []
        for row in rows:
            entity = await self._convert_to_entity(row)
            if entity:
                locations.append(entity)
        
        # Load type entities for each location
        if locations:
            # Group locations by type to minimize database calls
            locations_by_type = {}
            for location in locations:
                if location.location_type_id not in locations_by_type:
                    locations_by_type[location.location_type_id] = []
                locations_by_type[location.location_type_id].append(location)
            
            # Load type entities
            for type_id, locs in locations_by_type.items():
                type_entity = await self.type_repository.get_by_id(type_id)
                if type_entity:
                    for location in locs:
                        location.location_type = type_entity
        
        return locations

    async def get_with_full_data(self, location_id: UUID) -> Optional[LocationEntityPydantic]:
        """Get a location with all related data including buildings, resources, travel connections."""
        # Get the basic location first
        location = await self.get_by_id(location_id)
        if not location:
            return None
        
        # TODO: Add methods to fetch buildings, resources, travel connections
        # This will be expanded once we have the related repositories/services
        
        return location