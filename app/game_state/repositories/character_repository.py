# No need to import Boolean
from app.db.models.character import Character
from app.game_state.entities.resource.resource_pydantic import ResourceEntityPydantic
from app.game_state.entities.character.character_pydantic import CharacterEntityPydantic
from app.game_state.repositories.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

class CharacterRepository(BaseRepository[CharacterEntityPydantic, Character, UUID]):
    """
    Repository specifically for Character entities. Needs entity_cls for conversion.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model_cls=Character, entity_cls=CharacterEntityPydantic) # Pass entity_cls

    async def add_resources(self, character_id: UUID, resource_id: list[ResourceEntityPydantic]) -> bool:
        """
        Add resource(s) to character
        arguments: character_id, resource_id, amount
        response: None
        """
        pass