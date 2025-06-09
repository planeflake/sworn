import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.services.core.base_service import BaseService
from app.api.schemas.location.location_sub_types import LocationSubtypeCreate, LocationSubtypeUpdate, LocationSubTypeResponse
from app.game_state.repositories.location.location_sub_type_repository import LocationSubtypeRepository
from app.game_state.entities.geography.location_sub_type import LocationSubtype


class LocationSubTypeService(BaseService[LocationSubtype, LocationSubtypeCreate, LocationSubTypeResponse]):
    """Service layer for location subtype business logic"""

    def __init__(self, db: AsyncSession):
        repository = LocationSubtypeRepository(db)
        super().__init__(
            db=db,
            repository=repository,
            entity_class=LocationSubtype,
            response_class=LocationSubTypeResponse
        )
        self.logger = logging.getLogger(__name__)

    async def create_subtype(self, subtype_data: LocationSubtypeCreate) -> LocationSubtype:
        """Create a new location subtype with validation"""
        self.logger.info(f"Creating location subtype: {subtype_data.code}")

        # Check if code already exists
        existing = await self.repository.get_by_code(subtype_data.code)
        if existing:
            raise ValueError(f"Location subtype with code '{subtype_data.code}' already exists")

        # Convert to entity and create
        subtype_entity = LocationSubtype(**subtype_data.model_dump())
        created_subtype = await self.repository.create(subtype_entity)

        logging.info(f"Created subtype entity: {created_subtype}")

        self.logger.info(f"Successfully created location subtype: {created_subtype.code}")
        return created_subtype

    async def get_subtype_by_id(self, subtype_id: UUID) -> Optional[LocationSubtype]:
        """Get location subtype by ID"""
        return await self.repository.find_by_id(subtype_id)

    async def get_subtype_by_code(self, code: str) -> Optional[LocationSubtype]:
        """Get location subtype by code"""
        return await self.repository.get_by_code(code)

    async def update_subtype(self, subtype_id: UUID, update_data: LocationSubtypeUpdate) -> Optional[LocationSubtype]:
        """Update location subtype"""
        self.logger.info(f"Updating location subtype: {subtype_id}")

        # If code is being updated, check it doesn't conflict
        if update_data.code:
            existing = await self.repository.get_by_code(update_data.code)
            if existing and existing.id != subtype_id:
                raise ValueError(f"Location subtype with code '{update_data.code}' already exists")

        updated_subtype = await self.repository.update_entity(subtype_id, update_data)

        if updated_subtype:
            self.logger.info(f"Successfully updated location subtype: {subtype_id}")
        else:
            self.logger.warning(f"Location subtype not found for update: {subtype_id}")

        return updated_subtype

    async def delete_subtype(self, subtype_id: UUID) -> bool:
        """Delete location subtype"""
        self.logger.info(f"Deleting location subtype: {subtype_id}")

        success = await self.repository.delete(subtype_id)

        if success:
            self.logger.info(f"Successfully deleted location subtype: {subtype_id}")
        else:
            self.logger.warning(f"Location subtype not found for deletion: {subtype_id}")

        return success

    async def get_subtypes_by_location_type(self, location_type_id: UUID) -> List[LocationSubtype]:
        """Get all subtypes for a location type"""
        return await self.repository.find_by_location_type(location_type_id)

    async def get_subtypes_by_theme(self, theme_id: UUID) -> List[LocationSubtype]:
        """Get all subtypes for a theme"""
        return await self.repository.find_by_theme(theme_id)

    async def get_subtypes_by_location_type_and_theme(
            self,
            location_type_id: UUID,
            theme_id: UUID
    ) -> List[LocationSubtype]:
        """Get subtypes for specific location type and theme combination"""
        return await self.repository.find_by_location_type_and_theme(location_type_id, theme_id)

    async def get_subtypes_by_rarity(self, rarity: str) -> List[LocationSubtype]:
        """Get subtypes by rarity level"""
        return await self.repository.find_by_rarity(rarity)

    async def search_subtypes(
            self,
            location_type_id: Optional[UUID] = None,
            theme_id: Optional[UUID] = None,
            rarity: Optional[str] = None,
            tags: Optional[List[str]] = None,
            match_all_tags: bool = False,
            skip: int = 0,
            limit: int = 100
    ) -> Dict[str, Any]:
        """Search subtypes with multiple filters"""
        return await self.repository.find_with_filters(
            location_type_id=location_type_id,
            theme_id=theme_id,
            rarity=rarity,
            tags=tags,
            match_all_tags=match_all_tags,
            skip=skip,
            limit=limit
        )

    async def bulk_create_subtypes(self, subtypes_data: List[LocationSubtypeCreate]) -> List[LocationSubtype]:
        """Bulk create location subtypes"""
        self.logger.info(f"Bulk creating {len(subtypes_data)} location subtypes")

        # Validate all codes are unique
        codes = [subtype.code for subtype in subtypes_data]
        if len(codes) != len(set(codes)):
            raise ValueError("Duplicate codes found in bulk create request")

        # Check for existing codes
        for subtype_data in subtypes_data:
            existing = await self.repository.get_by_code(subtype_data.code)
            if existing:
                raise ValueError(f"Location subtype with code '{subtype_data.code}' already exists")

        # Convert to entities and bulk save
        entities = [LocationSubtype(**data.model_dump()) for data in subtypes_data]
        created_subtypes = await self.repository.bulk_save(entities)

        self.logger.info(f"Successfully bulk created {len(created_subtypes)} location subtypes")
        return created_subtypes
