# --- START OF FILE app/game_state/services/theme_service.py ---
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, List # Added List
import logging
import dataclasses # Added dataclasses

# Import Repository, Domain Entity (and potentially an API Model for Theme)
from app.game_state.repositories.theme_repository import ThemeRepository
from app.game_state.entities.theme import Theme as ThemeEntity
# from app.game_state.models.theme import ThemeApiModel # Define if needed for API consistency

class ThemeService:
    def __init__(self, db: AsyncSession):
        """Initializes the ThemeService with a database session."""
        self.db = db
        # Correctly instantiate the repository
        self.repository = ThemeRepository(db=self.db)
        logging.debug("ThemeService initialized with ThemeRepository.")

    async def exists(self, theme_id: UUID) -> bool:
        """Check if a theme exists by ID."""
        logging.debug(f"[ThemeService] Checking existence for theme ID: {theme_id}")
        try:
            return await self.repository.exists(theme_id)
        except Exception as e:
            logging.error(f"[ThemeService] Error checking existence for theme {theme_id}: {e}", exc_info=True)
            return False # Assume not exists on error

    async def get_theme(self, theme_id: UUID) -> Optional[ThemeEntity]:
        """Get a theme domain entity by ID."""
        logging.debug(f"[ThemeService] Getting theme ID: {theme_id}")
        try:
            return await self.repository.find_by_id(theme_id)
        except Exception as e:
            logging.error(f"[ThemeService] Error getting theme {theme_id}: {e}", exc_info=True)
            return None

    async def get_theme_by_name(self, name: str) -> Optional[ThemeEntity]:
        """Get a theme domain entity by name."""
        logging.debug(f"[ThemeService] Getting theme by name: {name}")
        try:
            return await self.repository.find_by_name(name)
        except Exception as e:
            logging.error(f"[ThemeService] Error getting theme by name '{name}': {e}", exc_info=True)
            return None

    async def create_theme(self, name: str, description: Optional[str] = None) -> Optional[ThemeEntity]:
        """Creates a new theme."""
        logging.info(f"[ThemeService] Creating theme with name: '{name}'")
        # Basic validation
        if not name:
            logging.error("[ThemeService] Theme name cannot be empty.")
            raise ValueError("Theme name cannot be empty.")

        # Check if theme name already exists
        existing_theme = await self.repository.find_by_name(name)
        if existing_theme:
             logging.warning(f"[ThemeService] Theme with name '{name}' already exists (ID: {existing_theme.id}).")
             # Decide whether to return existing or raise error
             raise ValueError(f"Theme with name '{name}' already exists.")
             # return existing_theme # Alternative: return existing one

        # Create domain entity instance
        theme_entity = ThemeEntity(name=name, description=description)
        logging.debug(f"[ThemeService] Created transient theme entity: {theme_entity}")

        try:
            # Save using repository
            saved_entity = await self.repository.save(theme_entity)
            logging.info(f"[ThemeService] Theme '{saved_entity.name}' created successfully with ID: {saved_entity.id}")
            return saved_entity
        except Exception as e:
            logging.exception(f"[ThemeService] Error saving new theme '{name}': {e}")
            # Consider specific DB error handling (e.g., constraint violations)
            raise # Re-raise after logging

    async def get_all_themes(self, skip: int = 0, limit: int = 100) -> List[ThemeEntity]:
        """Retrieves a list of theme domain entities."""
        logging.debug(f"[ThemeService] Getting all themes (skip={skip}, limit={limit})")
        try:
            return await self.repository.find_all(skip=skip, limit=limit)
        except Exception as e:
            logging.error(f"[ThemeService] Error getting all themes: {e}", exc_info=True)
            return []


# --- END OF FILE app/game_state/services/theme_service.py ---