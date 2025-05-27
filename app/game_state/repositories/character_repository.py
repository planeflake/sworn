# No need to import Boolean
from app.db.models.character import Character
from app.game_state.entities.resource import ResourceEntity
from app.game_state.entities.character import CharacterEntity
from app.game_state.repositories.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional #Any,List,Dict
from uuid import UUID


class CharacterRepository(BaseRepository[CharacterEntity, Character, UUID]):
    """
    Repository specifically for Character entities. Needs entity_cls for conversion.
    """
    def __init__(self, db: AsyncSession):
        # Pass both the DB model class AND the domain entity class to the base repository
        super().__init__(db=db, model_cls=Character, entity_cls=CharacterEntity) # Pass entity_cls

    async def add_resources(self, character_id: UUID, resource_id: list[ResourceEntity]) -> bool:
        """
        Add resource(s) to character
        arguments: character_id, resource_id, amount
        response: None
        """
        pass

    async def get_by_name(self, name: str) -> Optional[CharacterEntity]:
        return await self.get_by_field("name", name)
        
    async def _entity_to_model_dict(self, entity: CharacterEntity, is_new: bool = False) -> dict:
        """
        Override to handle special case of character_traits field being a list
        """
        model_dict = await super()._entity_to_model_dict(entity, is_new)

        # Ensure 'id' is included if 'entity_id' exists
        if 'id' not in model_dict and getattr(entity, "entity_id", None):
            model_dict["id"] = entity.entity_id

        # Handle character_traits which needs to be a list of enum values
        if hasattr(entity, "traits") and "character_traits" not in model_dict:
            model_dict["character_traits"] = entity.traits if entity.traits else []
            
        return model_dict
        
    async def _convert_to_entity(self, db_obj: Character) -> Optional[CharacterEntity]:
        """
        Override to handle special case of character_traits field
        """
        if db_obj is None:
            return None
            
        # Get the entity using the base implementation
        entity = await super()._convert_to_entity(db_obj)
        
        # Special handling for character_traits to traits mapping
        if entity is not None:
            if hasattr(db_obj, "character_traits") and db_obj.character_traits is not None:
                entity.traits = list(db_obj.character_traits)
                
        return entity