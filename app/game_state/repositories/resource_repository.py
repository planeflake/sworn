# --- START - app/game_state/repositories/resource_repository.py ---

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional

# Import base repository
from .base_repository import BaseRepository
# Import DB Model and Domain Entity
from app.db.models.resource import Resource as ResourceDbModel
from app.game_state.entities.resource import ResourceEntity
# Import Enums if needed for specific queries (less common here)
# from app.game_state.enums.shared import StatusEnum


# Define type hints for BaseRepository
# BaseRepository[DomainEntityType, DbModelType, PrimaryKeyType]
class ResourceRepository(BaseRepository[ResourceEntity, ResourceDbModel, UUID]):
    """
    Repository for handling Resource data persistence.
    """
    def __init__(self, db: AsyncSession):
        """
        Initializes the ResourceRepository.

        Args:
            db: The asynchronous SQLAlchemy session.
        """
        # Pass the specific DbModel and DomainEntity classes to the base
        super().__init__(
            db=db,
            model_cls=ResourceDbModel,
            entity_cls=ResourceEntity
            # pk_attr_name="resource_id" # Pass PK name if BaseRepository needs it explicitly
        )

    # --- Add Resource-Specific Query Methods Here ---

    async def find_by_name(self, name: str) -> Optional[ResourceEntity]:
        """Finds a resource type by its unique name."""
        # Assumes 'name' is unique in the DB model/table
        stmt = select(self.model_cls).where(self.model_cls.name == name)
        result = await self.db.execute(stmt)
        db_obj = result.scalars().first()
        return await self._convert_to_entity(db_obj)

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[ResourceEntity]:
        """Lists all defined resource types."""
        # Uses the find_all method inherited from BaseRepository
        return await super().find_all(skip=skip, limit=limit)

    # Example: Find resources by rarity
    # async def find_by_rarity(self, rarity: RarityEnum) -> List[ResourceEntity]:
    #     stmt = select(self.model_cls).where(self.model_cls.rarity == rarity)
    #     result = await self.db.execute(stmt)
    #     db_objs = result.scalars().all()
    #     return [await self._convert_to_entity(db_obj) for db_obj in db_objs]


# --- END - app/game_state/repositories/resource_repository.py ---