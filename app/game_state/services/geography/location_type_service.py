"""
Service for location types.
"""
from uuid import UUID, uuid4
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.services.core.base_service import BaseService
from app.game_state.entities.geography.location_type_pydantic import LocationTypeEntityPydantic
from app.game_state.repositories.location.location_type_repository import LocationTypeRepository
from app.api.schemas.location.location_type_schema import LocationTypeResponse, LocationTypeCreate, LocationTypeUpdate

class LocationTypeService(BaseService[LocationTypeEntityPydantic, LocationTypeCreate, LocationTypeResponse]):
    """Service for working with location types."""
    
    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        repository = LocationTypeRepository(db)
        super().__init__(
            db=db,
            repository=repository,
            entity_class=LocationTypeEntityPydantic,
            response_class=LocationTypeResponse
        )
    
    async def get_type(self, type_id: UUID) -> Optional[LocationTypeResponse]:
        """Get a location type by ID."""
        entity = await self.repository.get_by_id(type_id)
        if entity:
            return LocationTypeResponse.model_validate(entity.model_dump())
        return None
    
    async def get_type_by_code(self, code: str) -> Optional[LocationTypeResponse]:
        """Get a location type by code."""
        entity = await self.repository.get_by_code(code)
        if entity:
            return LocationTypeResponse.model_validate(entity.model_dump())
        return None
    
    async def get_all_types(self, theme: Optional[str] = None) -> List[LocationTypeResponse]:
        """Get all location types, optionally filtered by theme."""
        entities = await self.repository.get_all(theme)
        return [LocationTypeResponse.model_validate(entity.model_dump()) for entity in entities]
    
    async def create_type(self, create_data: LocationTypeCreate) -> LocationTypeResponse:
        """Create a new location type."""
        # Ensure code is unique
        existing = await self.repository.get_by_code(create_data.code)
        if existing:
            raise ValueError(f"Location type with code '{create_data.code}' already exists")
        
        # Create entity from schema data
        create_dict = create_data.model_dump(exclude={"id"})
        type_entity = LocationTypeEntityPydantic(
            id=uuid4(),
            **create_dict
        )
        
        # Save to database
        saved_entity = await self.repository.create(type_entity)
        return LocationTypeResponse.model_validate(saved_entity.to_dict())
    
    async def update_type(self, type_id: UUID, update_data: LocationTypeUpdate) -> Optional[LocationTypeResponse]:
        """Update an existing location type."""
        # Check if code is being changed and is unique
        update_dict = update_data.model_dump(exclude_unset=True)
        if "code" in update_dict:
            existing = await self.repository.get_by_id(type_id)
            if existing and update_dict["code"] != existing.code:
                code_check = await self.repository.get_by_code(update_dict["code"])
                if code_check:
                    raise ValueError(f"Location type with code '{update_dict['code']}' already exists")
        
        # Use centralized update method from base repository
        updated_entity = await self.repository.update_entity(type_id, update_data)
        if updated_entity:
            return LocationTypeResponse.model_validate(updated_entity.model_dump())
        return None
    
    async def delete_type(self, type_id: UUID) -> bool:
        """Delete a location type if not in use."""
        return await self.repository.delete(type_id)
    
    async def validate_containment(self, parent_type_id: UUID, child_type_id: UUID) -> bool:
        """Validate that a parent type can contain a child type."""
        parent_type = await self.repository.get_by_id(parent_type_id)
        child_type = await self.repository.get_by_id(child_type_id)
        
        if not parent_type or not child_type:
            return False
        
        return parent_type.can_contain_type(child_type.code)