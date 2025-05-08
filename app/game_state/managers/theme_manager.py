"""
Theme Manager - Contains domain logic for world operations
"""
from app.game_state.entities.theme import Theme
from app.game_state.repositories.theme_repository import ThemeRepository
from app.game_state.managers.base_manager import BaseManager
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import Optional

class ThemeManager:
    """Manager class for theme-specific domain logic"""
    
    @staticmethod
    async def create_theme(theme_id: Optional[str] = None, name: Optional[str] = None, description: Optional[str] = 0, db=AsyncSession) -> Theme:
        """
        Create a new world entity with default values.
        
        Args:
            world_id: Optional custom ID for the world
            
        Returns:
            A new WorldEntity instance
        """
        # Use the generic BaseManager.create method
        theme = BaseManager.create(
            entity_class=Theme,
            id=theme_id,
            name=name,
            description=description
        )

        await ThemeRepository.save(theme,db)  # Save the theme to the repository
        return theme