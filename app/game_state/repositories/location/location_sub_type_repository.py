from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.game_state.repositories.base_repository import BaseRepository
from app.db.models.location_sub_type import LocationSubType
from app.game_state.entities.geography.location_sub_type import LocationSubtype


class LocationSubtypeRepository(BaseRepository[LocationSubtype, LocationSubType, UUID]):
    """Repository for Location Subtype data access operations"""

    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model_cls=LocationSubType, entity_cls=LocationSubtype)

    async def get_by_code(self, code: str) -> Optional[LocationSubtype]:
        """Get location subtype by unique code with relationships loaded"""
        stmt = (
            select(self.model_cls)
            .options(
                selectinload(LocationSubType.location_type),
                selectinload(LocationSubType.theme)
            )
            .where(LocationSubType.code == code)
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        return await self._convert_to_entity(db_obj) if db_obj else None

    async def find_by_location_type(self, location_type_id: UUID) -> List[LocationSubtype]:
        """Get all subtypes for a specific location type"""
        stmt = (
            select(self.model_cls)
            .options(
                selectinload(LocationSubType.location_type),
                selectinload(LocationSubType.theme)
            )
            .where(LocationSubType.location_type_id == location_type_id)
        )
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        return [entity for entity in entities if entity is not None]

    async def find_by_theme(self, theme_id: UUID) -> List[LocationSubtype]:
        """Get all subtypes for a specific theme"""
        stmt = (
            select(self.model_cls)
            .options(
                selectinload(LocationSubType.location_type),
                selectinload(LocationSubType.theme)
            )
            .where(LocationSubType.theme_id == theme_id)
        )
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        return [entity for entity in entities if entity is not None]

    async def find_by_location_type_and_theme(
            self,
            location_type_id: UUID,
            theme_id: UUID
    ) -> List[LocationSubtype]:
        """Get subtypes for specific location type and theme combination"""
        stmt = (
            select(self.model_cls)
            .options(
                selectinload(LocationSubType.location_type),
                selectinload(LocationSubType.theme)
            )
            .where(
                and_(
                    LocationSubType.location_type_id == location_type_id,
                    LocationSubType.theme_id == theme_id
                )
            )
        )
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        return [entity for entity in entities if entity is not None]

    async def find_by_rarity(self, rarity: str) -> List[LocationSubtype]:
        """Get all subtypes with specific rarity"""
        stmt = (
            select(self.model_cls)
            .options(
                selectinload(LocationSubType.location_type),
                selectinload(LocationSubType.theme)
            )
            .where(LocationSubType.rarity == rarity)
        )
        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        return [entity for entity in entities if entity is not None]

    async def find_by_tags(self, tags: List[str], match_all: bool = False) -> List[LocationSubtype]:
        """Find subtypes that have any (or all) of the specified tags"""
        stmt = select(self.model_cls).options(
            selectinload(LocationSubType.location_type),
            selectinload(LocationSubType.theme)
        )

        if match_all:
            # All tags must be present
            for tag in tags:
                stmt = stmt.where(LocationSubType.tags.contains([tag]))
        else:
            # Any tag can match
            stmt = stmt.where(LocationSubType.tags.overlap(tags))

        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        return [entity for entity in entities if entity is not None]

    async def find_with_filters(
            self,
            location_type_id: Optional[UUID] = None,
            theme_id: Optional[UUID] = None,
            rarity: Optional[str] = None,
            tags: Optional[List[str]] = None,
            match_all_tags: bool = False,
            skip: int = 0,
            limit: int = 100
    ) -> Dict[str, Any]:
        """Find subtypes with multiple filters and pagination"""
        stmt = select(self.model_cls).options(
            selectinload(LocationSubType.location_type),
            selectinload(LocationSubType.theme)
        )

        # Build conditions list using list comprehension and filtering
        conditions = [
            condition for condition in [
                LocationSubType.location_type_id == location_type_id if location_type_id else None,
                LocationSubType.theme_id == theme_id if theme_id else None,
                LocationSubType.rarity == rarity if rarity else None,
                LocationSubType.tags.overlap(tags) if tags and not match_all_tags else None,
            ] if condition is not None
        ]

        # Handle match_all_tags separately since it's a loop
        if tags and match_all_tags:
            conditions.extend(LocationSubType.tags.contains([tag]) for tag in tags)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Get total count
        count_stmt = select(func.count(LocationSubType.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))

        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar_one()

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs if db_obj]
        valid_entities = [entity for entity in entities if entity is not None]

        return {
            "items": valid_entities,
            "total": total_count,
            "limit": limit,
            "skip": skip,
        }
