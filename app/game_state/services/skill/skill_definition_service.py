# --- START OF FILE app/game_state/services/skill_definition_service.py ---

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone

from app.game_state.repositories.skill_definition_repository import SkillDefinitionRepository
from app.game_state.entities.skill.skill_definition_pydantic import SkillDefinitionEntityPydantic
from app.api.schemas.skill_definition_schema import (
    SkillDefinitionRead,
    SkillDefinitionCreate,
    SkillDefinitionUpdate,
)

class SkillDefinitionService:
    """Service layer for Skill Definition operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = SkillDefinitionRepository(db=self.db)

    @staticmethod
    async def _convert_entity_to_read_schema(
        entity: Optional[SkillDefinitionEntityPydantic]
    ) -> Optional[SkillDefinitionRead]:
        """Converts domain entity to Pydantic Read schema."""
        if entity is None:
            return None
        try:
            # Build a complete dictionary with fallbacks for required fields
            entity_dict = {
                'id': str(entity.entity_id),
                'name': entity.name,
                'description': getattr(entity, 'description', None),
                'max_level': getattr(entity, 'max_level', 100),
                'themes': getattr(entity, 'themes', []),
                'metadata': getattr(entity, 'metadata', {}),
                'created_at': getattr(entity, 'created_at', datetime.now(timezone.utc)),
                'updated_at': getattr(entity, 'updated_at', None)
            }
            
            # Explicitly log the dictionary to help debug
            logging.debug(f"Entity dict for schema validation: {entity_dict}")
            
            return SkillDefinitionRead.model_validate(entity_dict)
        except Exception as e:
            logging.error(f"Failed to convert SkillDefinitionEntity to Read schema: {e}", exc_info=True)
            logging.error(f"Entity data: {entity}")
            raise ValueError("Internal error converting skill definition data.") from e

    async def create_skill_definition(
        self, skill_data: SkillDefinitionCreate
    ) -> SkillDefinitionRead:
        """Creates a new skill definition."""
        logging.info(f"Attempting to create skill definition: {skill_data.name}")

        existing = await self.repository.find_by_name(skill_data.name)
        if existing:
            raise ValueError(f"Skill definition with name '{skill_data.name}' already exists.")

        transient_entity = SkillDefinitionEntityPydantic(
            name=skill_data.name,
            description=skill_data.description,
            max_level=skill_data.max_level,
            themes=skill_data.themes
            # skill_key=skill_data.skill_key # If using skill_key
        )

        try:
            saved_entity = await self.repository.save(transient_entity)
        except Exception as e:
            logging.error(f"Database error saving skill definition '{skill_data.name}': {e}", exc_info=True)
            raise ValueError(f"Could not save skill definition: {e}") from e

        read_schema = await self._convert_entity_to_read_schema(saved_entity)
        if read_schema is None:
             logging.error(f"Saved skill def {saved_entity.entity_id} but failed conversion.")
             raise ValueError("Internal error processing saved skill definition data.")

        logging.info(f"Successfully created skill definition: {read_schema.name} (ID: {read_schema.id})")
        return read_schema

    async def get_skill_definition(self, skill_definition_id: UUID) -> Optional[SkillDefinitionRead]:
        """Gets a single skill definition by ID."""
        logging.debug(f"Getting skill definition by ID: {skill_definition_id}")
        entity = await self.repository.find_by_id(skill_definition_id)
        return await self._convert_entity_to_read_schema(entity)

    async def get_skill_definition_by_name(self, name: str) -> Optional[SkillDefinitionRead]:
        """Gets a single skill definition by name."""
        logging.debug(f"Getting skill definition by name: {name}")
        entity = await self.repository.find_by_name(name)
        return await self._convert_entity_to_read_schema(entity)

    async def get_all_skill_definitions(self, skip: int = 0, limit: int = 100) -> List[SkillDefinitionRead]:
        """Gets a list of all skill definitions."""
        logging.debug(f"Getting all skill definitions (skip={skip}, limit={limit})")
        entities = await self.repository.find_all(skip=skip, limit=limit)
        return [
            schema for entity in entities
            if (schema := await self._convert_entity_to_read_schema(entity)) is not None
        ]

    async def update_skill_definition(
        self, skill_definition_id: UUID, update_data: SkillDefinitionUpdate
    ) -> Optional[SkillDefinitionRead]:
        """Updates an existing skill definition."""
        logging.info(f"Attempting to update skill definition ID: {skill_definition_id}")
        
        # Use centralized update method from base repository
        try:
            updated_entity = await self.repository.update_entity(skill_definition_id, update_data)
            if updated_entity:
                read_schema = await self._convert_entity_to_read_schema(updated_entity)
                if read_schema is None:
                    logging.error(f"Updated skill def {updated_entity.entity_id} but failed conversion.")
                    raise ValueError("Internal error processing updated skill definition data.")
                logging.info(f"Successfully updated skill definition: {read_schema.name} (ID: {read_schema.id})")
                return read_schema
            else:
                logging.warning(f"Skill definition not found for update: {skill_definition_id}")
                return None
        except Exception as e:
            logging.error(f"Database error updating skill definition ID {skill_definition_id}: {e}", exc_info=True)
            raise ValueError(f"Could not update skill definition: {e}") from e

    async def delete_skill_definition(self, skill_definition_id: UUID) -> bool:
        """Deletes a skill definition by ID."""
        logging.info(f"Attempting to delete skill definition ID: {skill_definition_id}")
        # Optional: Check if skill is used in profession requirements?
        deleted = await self.repository.delete(skill_definition_id)
        if not deleted:
            logging.warning(f"Skill definition not found for deletion: {skill_definition_id}")
        else:
            logging.info(f"Successfully deleted skill definition: {skill_definition_id}")
        return deleted

# --- END OF FILE app/game_state/services/skill_definition_service.py ---