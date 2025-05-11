# --- START OF FILE app/game_state/services/building_blueprint_service.py ---

import logging
import uuid
from typing import List, Optional
import dataclasses
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.repositories.building_blueprint_repository import BuildingBlueprintRepository
from app.game_state.managers.building_blueprint_manager import BuildingBlueprintManager
from app.game_state.entities.building_blueprint import BuildingBlueprintEntity
from app.api.schemas.building_blueprint_schema import (
    BuildingBlueprintRead,
    BuildingBlueprintCreate,
    BuildingBlueprintUpdate,
)
# from app.game_state.services.theme_service import ThemeService # For validation

class BuildingBlueprintService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = BuildingBlueprintRepository(db=self.db)
        self.manager = BuildingBlueprintManager()
        # self.theme_service = ThemeService(db=db) # For validating theme_id exists

    async def _convert_entity_to_read_schema(self, entity: Optional[BuildingBlueprintEntity]) -> Optional[BuildingBlueprintRead]:
        if entity is None:
            return None
        try:
            entity_dict = dataclasses.asdict(entity)
            if 'entity_id' in entity_dict and 'id' not in entity_dict: # Map entity_id to id for schema
                entity_dict['id'] = entity_dict.pop('entity_id')
            
            # Handle _metadata alias for schema output
            if 'metadata_' in entity_dict and '_metadata' not in entity_dict:
                entity_dict['_metadata'] = entity_dict.pop('metadata_')

            # Recursively convert stages and features if not handled by Pydantic's from_attributes
            # This is often complex; Pydantic's from_attributes with nested Read schemas should ideally handle it.
            # If direct asdict doesn't nest correctly for Read schemas, manual conversion is needed.
            # For now, assume Pydantic handles nested Read schemas from nested entity objects.

            return BuildingBlueprintRead.model_validate(entity_dict)
        except Exception as e:
            logging.error(f"Failed to convert BuildingBlueprintEntity to Read schema: {e}", exc_info=True)
            logging.error(f"Entity data: {entity}")
            raise ValueError("Internal error converting blueprint data.")

    async def create_blueprint(self, blueprint_data: BuildingBlueprintCreate) -> BuildingBlueprintRead:
        logging.info(f"Attempting to create blueprint: {blueprint_data.name}")

        # --- Validation ---
        # 1. Validate Theme ID exists
        # if not await self.theme_service.theme_exists(blueprint_data.theme_id):
        #     raise ValueError(f"Theme with ID {blueprint_data.theme_id} not found.")

        # 2. Validate unique name (optionally per theme)
        existing_by_name = await self.repository.find_by_name(name=blueprint_data.name, theme_id=blueprint_data.theme_id)
        if existing_by_name:
            raise ValueError(f"Building blueprint with name '{blueprint_data.name}' already exists (for this theme).")

        # 3. Validate stages (e.g., sequential stage_number, at least one stage)
        if not blueprint_data.stages:
            raise ValueError("Building blueprint must have at least one stage.")
        stage_numbers = {s.stage_number for s in blueprint_data.stages}
        if len(stage_numbers) != len(blueprint_data.stages):
            raise ValueError("Stage numbers must be unique within a blueprint.")
        # Check for sequential numbering if required, e.g. min stage is 1 and max is len(stages)
        # ... more complex stage/feature validation can go here or in the manager ...

        transient_entity = self.manager.create_transient_blueprint(schema_data=blueprint_data)
        
        try:
            # Use the specialized save method in the repository for full blueprint
            saved_entity = await self.repository.save_blueprint_with_stages(transient_entity)
        except Exception as e:
            logging.error(f"Database error saving blueprint '{blueprint_data.name}': {e}", exc_info=True)
            raise ValueError(f"Could not save building blueprint: {e}")

        read_schema = await self._convert_entity_to_read_schema(saved_entity)
        if read_schema is None:
            raise ValueError("Internal error processing saved blueprint data.")
        
        logging.info(f"Successfully created blueprint: {read_schema.name} (ID: {read_schema.id})")
        return read_schema

    async def get_blueprint_entity(self, blueprint_id: uuid.UUID) -> Optional[BuildingBlueprintEntity]:
        """Returns the domain entity, not the read schema."""
        return await self.repository.find_by_id_with_details(blueprint_id)

    async def get_blueprint(self, blueprint_id: uuid.UUID) -> Optional[BuildingBlueprintRead]:
        entity = await self.repository.find_by_id_with_details(blueprint_id)
        return await self._convert_entity_to_read_schema(entity)

    async def get_all_blueprints(self, skip: int = 0, limit: int = 100, theme_id: Optional[uuid.UUID] = None) -> List[BuildingBlueprintRead]:
        entities = await self.repository.find_all_with_details(skip=skip, limit=limit, theme_id=theme_id)
        return [schema for entity in entities if (schema := await self._convert_entity_to_read_schema(entity)) is not None]

    async def update_blueprint(self, blueprint_id: uuid.UUID, update_data: BuildingBlueprintUpdate) -> Optional[BuildingBlueprintRead]:
        logging.info(f"Attempting to update blueprint ID: {blueprint_id}")
        entity = await self.repository.find_by_id_with_details(blueprint_id) # Fetch with details
        if not entity:
            return None

        update_dict = update_data.model_dump(exclude_unset=True, by_alias=True) # Use by_alias for _metadata
        
        updated_fields = False
        for key, value in update_dict.items():
            # Handle aliased field '_metadata' which maps to 'metadata_' on entity
            entity_key = key
            if key == "_metadata": # from schema (aliased)
                entity_key = "metadata_" # on entity
            
            if hasattr(entity, entity_key) and getattr(entity, entity_key) != value:
                setattr(entity, entity_key, value)
                updated_fields = True
        
        if not updated_fields:
            logging.info(f"No changes detected for blueprint {blueprint_id}.")
            return await self._convert_entity_to_read_schema(entity)

        entity.updated_at = datetime.now(timezone.utc)

        try:
            # For simple updates not affecting stages, the base save might work
            # But if stages were part of update_data (they are not in BuildingBlueprintUpdate),
            # you'd call save_blueprint_with_stages
            saved_entity = await self.repository.save(entity) # This save only updates top-level blueprint fields
        except Exception as e:
            logging.error(f"Database error updating blueprint '{entity.name}': {e}", exc_info=True)
            raise ValueError(f"Could not update blueprint: {e}")
            
        # After saving, refetch with details to ensure the response is complete if stages were involved implicitly
        # For this simple update, saved_entity might be sufficient if it was refreshed by repo.save()
        # But to be safe, or if stages could be affected by metadata changes indirectly:
        refetched_entity = await self.repository.find_by_id_with_details(saved_entity.entity_id)
        return await self._convert_entity_to_read_schema(refetched_entity)


    async def delete_blueprint(self, blueprint_id: uuid.UUID) -> bool:
        # Add checks: e.g., is this blueprint used by any BuildingInstances?
        # If so, prevent deletion or handle cascading (e.g., mark instances as "orphaned").
        # For now, simple delete. Cascades in DB model should handle stages/features.
        logging.info(f"Attempting to delete blueprint ID: {blueprint_id}")
        deleted = await self.repository.delete(blueprint_id) # Base delete
        if deleted:
            logging.info(f"Successfully deleted blueprint: {blueprint_id}")
        else:
            logging.warning(f"Blueprint not found for deletion: {blueprint_id}")
        return deleted

# --- END OF FILE app/game_state/services/building_blueprint_service.py ---