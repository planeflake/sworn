from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID

from app.db.models.action_category import ActionCategory
from app.game_state.entities.action.action_category_pydantic import ActionCategoryPydantic
from .base_repository import BaseRepository


class ActionCategoryRepository(BaseRepository[ActionCategoryPydantic, ActionCategory, UUID]):
    """Repository for managing action categories with hierarchical structure."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ActionCategory, ActionCategoryPydantic)
    
    async def get_root_categories(self) -> List[ActionCategoryPydantic]:
        """Get all root categories (categories with no parent)."""
        stmt = select(ActionCategory).where(ActionCategory.parent_category_id.is_(None))
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self.model_to_entity(model) for model in models]
    
    async def get_children_of_category(self, parent_id: UUID) -> List[ActionCategoryPydantic]:
        """Get all child categories of a given parent category."""
        stmt = select(ActionCategory).where(ActionCategory.parent_category_id == parent_id)
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self.model_to_entity(model) for model in models]
    
    async def get_category_with_children(self, category_id: UUID) -> Optional[ActionCategoryPydantic]:
        """Get a category with its immediate children populated."""
        category = await self.get_by_id(category_id)
        if category:
            children = await self.get_children_of_category(category_id)
            category.child_categories = children
        return category