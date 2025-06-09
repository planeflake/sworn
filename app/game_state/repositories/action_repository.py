from app.db.models.character_action import CharacterAction
from app.game_state.entities.action.character_action_pydantic import CharacterActionPydantic
from app.game_state.repositories.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

class ActionRepository(BaseRepository[CharacterActionPydantic, CharacterAction, UUID]):
    """Repository for character actions - follows your base repository pattern."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model_cls=CharacterAction, entity_cls=CharacterActionPydantic)

    async def get_actions_by_character(self, character_id: UUID) -> List[CharacterActionPydantic]:
        """Get all actions for a specific character."""
        return await self.find_by_field_list("character_id", [character_id])
    
    async def get_active_actions_by_character(self, character_id: UUID) -> List[CharacterActionPydantic]:
        """Get all active (queued or in-progress) actions for a character."""
        from app.game_state.entities.action.character_action_pydantic import ActionStatus
        
        # This would need to be implemented in base repository for multiple field matching
        # For now, simplified approach
        all_actions = await self.get_actions_by_character(character_id)
        return [
            action for action in all_actions 
            if action.status in [ActionStatus.QUEUED, ActionStatus.IN_PROGRESS]
        ]