# --- START OF FILE app/game_state/services/profession_service.py ---

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from app.game_state.repositories.profession_repository import ProfessionRepository
from app.game_state.managers.profession_definition_manager import ProfessionManager
from app.api.schemas.profession_schema import (
    ProfessionDefinitionRead,
    ProfessionDefinitionCreate,
    ProfessionDefinitionUpdate,
)
# Import ThemeService if validation is needed (e.g., check themes exist)
# from .theme_service import ThemeService

class ProfessionService:
    """Service layer for Profession Definition operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ProfessionRepository(db=self.db)
        self.manager = ProfessionManager
        # self.theme_service = ThemeService(db=self.db) # Optional: for validation

    async def create_profession(
        self, profession_data: ProfessionDefinitionCreate
    ) -> ProfessionDefinitionRead:
        """Creates a new profession definition."""
        logging.info(f"Attempting to create profession: {profession_data.name}")

        # Optional: Add validation (e.g., check if name already exists, check themes)
        existing = await self.repository.find_by_name(profession_data.name)
        if existing:
            raise ValueError(f"Profession definition with name '{profession_data.name}' already exists.")
        # await self.theme_service.validate_themes_exist(profession_data.available_theme_ids)

        # 1. Create the transient domain entity (can use Manager or direct instantiation)
        # Using direct instantiation for simplicity here, assuming Manager doesn't add much value for definitions yet

        transient_entity = self.manager.create(
            name=profession_data.name,  # Set BaseEntity name
            display_name=profession_data.display_name,
            description=profession_data.description,
            category=profession_data.category,
            skill_requirements=profession_data.skill_requirements,
            available_theme_ids=profession_data.available_theme_ids,
            valid_unlock_methods=profession_data.valid_unlock_methods,
            unlock_condition_details=profession_data.unlock_condition_details,
            python_class_override=profession_data.python_class_override,
            archetype_handler=profession_data.archetype_handler,
            configuration_data=profession_data.configuration_data,
        )

        # 2. Save using the repository
        try:
            saved_entity = await self.repository.save(transient_entity)
        except Exception as e:
            logging.error(f"Database error saving profession '{profession_data.name}': {e}", exc_info=True)
            raise ValueError(f"Could not save profession definition: {e}") from e

        # 3. Convert saved domain entity to Read Schema for response
        read_schema = ProfessionDefinitionRead.model_validate(saved_entity.to_dict())
        if read_schema is None:
             # This indicates an issue during conversion after successful save
             logging.error(f"Successfully saved profession {saved_entity.entity_id} but failed to convert to read schema.")
             raise ValueError("Internal error processing saved profession data.")

        logging.info(f"Successfully created profession: {read_schema.name} (ID: {read_schema.id})")
        return read_schema

    async def get_profession(self, profession_id: UUID) -> Optional[ProfessionDefinitionRead]:
        """Gets a single profession definition by ID."""
        logging.debug(f"Getting profession definition by ID: {profession_id}")
        entity = await self.repository.find_by_id(profession_id)
        return ProfessionDefinitionRead.model_validate(entity.to_dict()) if entity else None

    async def get_all_professions(self, skip: int = 0, limit: int = 100) -> List[ProfessionDefinitionRead]:
        """Gets a list of all profession definitions."""
        logging.debug(f"Getting all profession definitions (skip={skip}, limit={limit})")
        entities = await self.repository.find_all(skip=skip, limit=limit)
        return [ ProfessionDefinitionRead.model_validate(entity.to_dict()) for entity in entities ]

    async def update_profession(
        self, profession_id: UUID, update_data: ProfessionDefinitionUpdate
    ) -> Optional[ProfessionDefinitionRead]:
        """Updates an existing profession definition."""
        logging.info(f"Attempting to update profession ID: {profession_id}")
        
        # Use centralized update method from base repository
        try:
            updated_entity = await self.repository.update_entity(profession_id, update_data)
            if updated_entity:
                read_schema = ProfessionDefinitionRead.model_validate(updated_entity.to_dict())
                logging.info(f"Successfully updated profession: {read_schema.name} (ID: {read_schema.id})")
                return read_schema
            else:
                logging.warning(f"Profession definition not found for update: {profession_id}")
                return None
        except Exception as e:
            logging.error(f"Database error updating profession ID {profession_id}: {e}", exc_info=True)
            raise ValueError(f"Could not update profession definition: {e}") from e

    async def delete_profession(self, profession_id: UUID) -> bool:
        """Deletes a profession definition by ID."""
        logging.info(f"Attempting to delete profession ID: {profession_id}")
        # Optional: Check if the profession is in use before deleting?
        deleted = await self.repository.delete(profession_id)
        if not deleted:
            logging.warning(f"Profession definition not found for deletion: {profession_id}")
        else:
            logging.info(f"Successfully deleted profession definition: {profession_id}")
        return deleted

# --- END OF FILE app/game_state/services/profession_service.py ---