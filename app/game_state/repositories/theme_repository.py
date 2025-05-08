# --- START OF FILE app/game_state/repositories/theme_repository.py ---
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # Import select
from uuid import UUID
from typing import Optional # Import Optional
import logging # Import logging

from app.db.models.theme import Theme as ThemeModel # DB Model
from app.game_state.entities.theme import Theme as ThemeEntity # Domain Entity
from app.game_state.repositories.base_repository import BaseRepository

class ThemeRepository(BaseRepository[ThemeEntity, ThemeModel, UUID]):
    def __init__(self, db: AsyncSession):
        """Initializes the ThemeRepository."""
        # Pass the DB session, SQLAlchemy model, and Domain entity
        super().__init__(db=db, model_cls=ThemeModel, entity_cls=ThemeEntity)
        logging.info(f"ThemeRepository initialized with model {ThemeModel.__name__} and entity {ThemeEntity.__name__}")


    async def find_by_name(self, name: str) -> Optional[ThemeEntity]:
        """Finds a theme by its unique name."""
        logging.debug(f"[ThemeRepository] Finding theme by name: {name}")
        stmt = select(self.model_cls).where(self.model_cls.name == name)
        result = await self.db.execute(stmt)
        db_obj = result.scalars().first()
        if db_obj:
            logging.debug(f"[ThemeRepository] Found theme by name: {name}, ID: {db_obj.id}")
            return await self._convert_to_entity(db_obj)
        else:
            logging.debug(f"[ThemeRepository] Theme not found by name: {name}")
            return None

    # Add other theme-specific repository methods if needed

# --- END OF FILE app/game_state/repositories/theme_repository.py ---