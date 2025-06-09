from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID

from app.db.models.tool_tier import ToolTier
from app.game_state.entities.core.tool_tier_pydantic import ToolTierPydantic
from .base_repository import BaseRepository


class ToolTierRepository(BaseRepository[ToolTierPydantic, ToolTier, UUID]):
    """Repository for managing tool tiers with theme-specific queries."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ToolTier, ToolTierPydantic)
    
    async def get_by_theme(self, theme_id: UUID) -> List[ToolTierPydantic]:
        """Get all tool tiers for a specific theme, ordered by tier level."""
        stmt = select(ToolTier).where(ToolTier.theme_id == theme_id).order_by(ToolTier.tier_level)
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        entities = []
        for model in models:
            entity = await self._convert_to_entity(model)
            if entity:
                entities.append(entity)
        return entities
    
    async def get_by_theme_and_level(self, theme_id: UUID, tier_level: int) -> Optional[ToolTierPydantic]:
        """Get a specific tool tier by theme and level."""
        stmt = select(ToolTier).where(
            and_(
                ToolTier.theme_id == theme_id,
                ToolTier.tier_level == tier_level
            )
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return await self._convert_to_entity(model) if model else None
    
    async def get_progression_for_theme(self, theme_id: UUID) -> List[ToolTierPydantic]:
        """Get the complete tool tier progression for a theme."""
        return await self.get_by_theme(theme_id)
    
    async def get_max_tier_for_theme(self, theme_id: UUID) -> Optional[ToolTierPydantic]:
        """Get the highest tier available for a theme."""
        stmt = select(ToolTier).where(ToolTier.theme_id == theme_id).order_by(ToolTier.tier_level.desc()).limit(1)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return await self._convert_to_entity(model) if model else None
    
    async def get_basic_tier_for_theme(self, theme_id: UUID) -> Optional[ToolTierPydantic]:
        """Get the basic (tier 1) tool tier for a theme."""
        return await self.get_by_theme_and_level(theme_id, 1)
    
    async def get_tiers_by_tech_level(self, theme_id: UUID, tech_level: int) -> List[ToolTierPydantic]:
        """Get all tool tiers available at a specific tech level for a theme."""
        stmt = select(ToolTier).where(
            and_(
                ToolTier.theme_id == theme_id,
                ToolTier.required_tech_level <= tech_level
            )
        ).order_by(ToolTier.tier_level)
        
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self.model_to_entity(model) for model in models]