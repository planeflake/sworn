from typing import List
from uuid import UUID
from app.api.schemas.tool_tier_schema import ToolTierResponseSchema
from app.game_state.repositories.tool_tier_repository import ToolTierRepository

class ToolTierService:
    def __init__(self, db):
        self.db = db
        self.repository = ToolTierRepository(db)

    async def find_all(self) -> List[ToolTierResponseSchema]:

        tool_tiers = await self.repository.find_all()

        return [ToolTierResponseSchema.model_dump(tool_tier) for tool_tier in tool_tiers]

    async def find_by_id(self, uuid: UUID) -> ToolTierResponseSchema:

        tool_tier = await self.repository.find_by_id(uuid)

        return ToolTierResponseSchema.model_dump(tool_tier)
