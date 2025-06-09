from app.game_state.services.core.base_service import BaseService
from app.game_state.repositories.faction_repository import FactionRepository
from app.api.schemas.faction_schema import FactionResponse
from app.game_state.entities.faction.faction_pydantic import FactionEntityPydantic

class FactionService(BaseService):
    def __init__(self, db):
        super().__init__(
            db=db,
            repository=FactionRepository(db),
            entity_class=FactionEntityPydantic,
            response_class=FactionResponse
        )

    async def create_faction(self, faction_data):
        faction = FactionEntityPydantic.model_validate(faction_data)
        return await self.repository.create(faction)

    async def find_all(self):
        factions = await self.repository.find_all()
        return factions