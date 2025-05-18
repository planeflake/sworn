# --- START OF FILE app/game_state/services/profession_service.py ---

import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from app.game_state.repositories.profession_repository import ProfessionRepository
from app.game_state.managers.profession_definition_manager import ProfessionManager # Optional: Use if create logic is complex
from app.game_state.entities.profession_definition_entity import ProfessionDefinitionEntity
from app.game_state.schemas.profession_schema import ( # Import API Schemas
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

    @staticmethod
    async def _convert_entity_to_read_schema(
        entity: Optional[ProfessionDefinitionEntity]
    ) -> Optional[ProfessionDefinitionRead]:
        """Converts domain entity to Pydantic Read schema."""
        if entity is None:
            return None
        try:
            # Instead of relying on to_dict, create a minimal dict with just the fields we need
            entity_dict = {
                'id': str(entity.entity_id),
                'name': entity.name,
                'display_name': getattr(entity, 'display_name', entity.name),
                'created_at': datetime.now(timezone.utc)  # Use current time as a fallback
            }
            
            # Add optional fields if they exist
            if hasattr(entity, 'description') and entity.description is not None:
                entity_dict['description'] = entity.description
                
            if hasattr(entity, 'category') and entity.category is not None:
                entity_dict['category'] = entity.category
                
            # Fix for skill_requirements: Check if it's a Field object
            if hasattr(entity, 'skill_requirements'):
                if hasattr(entity.skill_requirements, 'default_factory') and callable(entity.skill_requirements.default_factory):
                    # If it's a dataclass Field object, use an empty list
                    entity_dict['skill_requirements'] = []
                else:
                    entity_dict['skill_requirements'] = entity.skill_requirements or []
                
            # Fix for available_theme_ids: Check if it's a Field object
            if hasattr(entity, 'available_theme_ids'):
                if hasattr(entity.available_theme_ids, 'default_factory') and callable(entity.available_theme_ids.default_factory):
                    # If it's a dataclass Field object, use an empty list
                    entity_dict['available_theme_ids'] = []
                else:
                    theme_ids = entity.available_theme_ids or []
                    # Convert UUIDs to strings
                    entity_dict['available_theme_ids'] = [str(theme_id) if isinstance(theme_id, uuid.UUID) else theme_id 
                                                      for theme_id in theme_ids]
                
            # Fix for valid_unlock_methods: Check if it's a Field object
            if hasattr(entity, 'valid_unlock_methods'):
                if hasattr(entity.valid_unlock_methods, 'default_factory') and callable(entity.valid_unlock_methods.default_factory):
                    # If it's a dataclass Field object, use an empty list
                    entity_dict['valid_unlock_methods'] = []
                else:
                    entity_dict['valid_unlock_methods'] = entity.valid_unlock_methods or []
                
            # Fix for unlock_condition_details: Check if it's a Field object
            if hasattr(entity, 'unlock_condition_details'):
                if hasattr(entity.unlock_condition_details, 'default_factory') and callable(entity.unlock_condition_details.default_factory):
                    # If it's a dataclass Field object, use an empty list
                    entity_dict['unlock_condition_details'] = []
                else:
                    entity_dict['unlock_condition_details'] = entity.unlock_condition_details or []
                
            if hasattr(entity, 'python_class_override'):
                entity_dict['python_class_override'] = entity.python_class_override
                
            if hasattr(entity, 'archetype_handler'):
                entity_dict['archetype_handler'] = entity.archetype_handler
                
            # Fix for configuration_data: Check if it's a Field object
            if hasattr(entity, 'configuration_data'):
                if hasattr(entity.configuration_data, 'default_factory') and callable(entity.configuration_data.default_factory):
                    # If it's a dataclass Field object, use an empty dict
                    entity_dict['configuration_data'] = {}
                else:
                    entity_dict['configuration_data'] = entity.configuration_data or {}
                
            if hasattr(entity, 'updated_at') and entity.updated_at is not None:
                if isinstance(entity.updated_at, datetime):
                    entity_dict['updated_at'] = entity.updated_at
            
            # Additional logging to verify field contents
            logging.debug(f"Final entity dict for schema validation: {entity_dict}")
            
            # Validate and convert to Pydantic schema
            return ProfessionDefinitionRead.model_validate(entity_dict)
        except Exception as e:
            logging.error(f"Failed to convert ProfessionDefinitionEntity to Read schema: {e}", exc_info=True)
            logging.error(f"Entity data: {entity}")
            #logging.error(f"Entity dict for schema conversion: {entity_dict if 'entity_dict' in locals() else 'N/A'}")
            # In production, you might want a more generic error
            raise ValueError("Internal error converting profession data.") from e

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
        read_schema = await self._convert_entity_to_read_schema(saved_entity)
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
        return await self._convert_entity_to_read_schema(entity)

    async def get_all_professions(self, skip: int = 0, limit: int = 100) -> List[ProfessionDefinitionRead]:
        """Gets a list of all profession definitions."""
        logging.debug(f"Getting all profession definitions (skip={skip}, limit={limit})")
        entities = await self.repository.find_all(skip=skip, limit=limit)
        return [
            schema for entity in entities
            if (schema := await self._convert_entity_to_read_schema(entity)) is not None
        ]

    async def update_profession(
        self, profession_id: UUID, update_data: ProfessionDefinitionUpdate
    ) -> Optional[ProfessionDefinitionRead]:
        """Updates an existing profession definition."""
        logging.info(f"Attempting to update profession ID: {profession_id}")
        entity = await self.repository.find_by_id(profession_id)
        if not entity:
            logging.warning(f"Profession definition not found for update: {profession_id}")
            return None

        # Convert Pydantic update data to dict, excluding unset fields
        update_dict = update_data.model_dump(exclude_unset=True)

        # Update the domain entity's fields
        updated = False
        for key, value in update_dict.items():
            if hasattr(entity, key) and getattr(entity, key) != value:
                setattr(entity, key, value)
                updated = True

        if not updated:
            logging.info(f"No changes detected for profession {profession_id}.")
            return await self._convert_entity_to_read_schema(entity) # Return current state

        # Save the updated entity
        try:
            saved_entity = await self.repository.save(entity)
        except Exception as e:
            logging.error(f"Database error updating profession '{entity.name}': {e}", exc_info=True)
            raise ValueError(f"Could not update profession definition: {e}") from e

        read_schema = await self._convert_entity_to_read_schema(saved_entity)
        if read_schema is None:
             logging.error(f"Successfully updated profession {saved_entity.entity_id} but failed to convert to read schema.")
             raise ValueError("Internal error processing updated profession data.")

        logging.info(f"Successfully updated profession: {read_schema.name} (ID: {read_schema.id})")
        return read_schema

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