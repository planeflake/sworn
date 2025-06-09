"""
Theme Manager - Contains domain logic for theme operations
"""
from uuid import UUID
from app.game_state.entities.core.theme_pydantic import ThemeEntityPydantic
from app.game_state.repositories.theme_repository import ThemeRepository
from app.game_state.managers.base_manager import BaseManager
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import Optional

class ThemeManager:
    """Manager class for theme-specific domain logic"""
    
    @staticmethod
    async def create_theme(theme_id: Optional[UUID] = None, name: Optional[str] = None, description: Optional[str] = None, db: AsyncSession = None) -> ThemeEntityPydantic:
        """
        Create a new theme entity with the specified values.
        
        Args:
            theme_id: Optional custom ID for the theme
            name: Name of the theme
            description: Description of the theme
            db: Database session
            
        Returns:
            A new ThemeEntityPydantic instance
        """
        # Use the generic BaseManager.create method
        theme = BaseManager.create(
            entity_class=ThemeEntityPydantic,
            entity_id=theme_id,
            name=name,
            description=description
        )

        # Save the theme to the repository if db session is provided
        if db:
            repo = ThemeRepository(db)
            theme = await repo.save(theme)
            
        return theme