from sqlalchemy import Boolean
from app.db.models.character import Character
from app.game_state.entities.resource import ResourceEntity
from app.game_state.entities.character import CharacterEntity
from app.game_state.repositories.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional #Any,List,Dict
from uuid import UUID


class CharacterRepository(BaseRepository[CharacterEntity, Character, UUID]):
    """
    Repository specifically for Settlement entities. Needs entity_cls for conversion.
    """
    def __init__(self, db: AsyncSession):
        # Pass both the DB model class AND the domain entity class to the base repository
        super().__init__(db=db, model_cls=Character, entity_cls=CharacterEntity) # Pass entity_cls

    async def add_resources(self,character_id:UUID,resource_id:list[ResourceEntity]) -> Boolean:
        """
        Add resource(s) to character
        arguments: character_id, resource_id, amount
        response: None
        """
        pass

    async def get_by_name(self, name: str) -> Optional[CharacterEntity]:
        return await self.get_by_field("name", name)