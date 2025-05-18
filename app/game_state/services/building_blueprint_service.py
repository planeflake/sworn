# --- START OF FILE app/game_state/services/building_blueprint_service.py ---

import logging
import uuid
from typing import List, Optional, Any, Dict
import dataclasses
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.repositories.building_blueprint_repository import BuildingBlueprintRepository
from app.game_state.managers.building_blueprint_manager import BuildingBlueprintManager
from app.game_state.entities.building_blueprint import BuildingBlueprintEntity
from app.game_state.services.theme_service import ThemeService 
from app.api.schemas.building_blueprint_schema import (
    BuildingBlueprintRead,
    BuildingBlueprintCreate,
    BuildingBlueprintUpdate,
)

class BuildingBlueprintService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = BuildingBlueprintRepository(db=self.db)
        self.manager = BuildingBlueprintManager()
        self.theme_service = ThemeService(db=db)

    async def _convert_entity_to_read_schema(self, entity: Optional[BuildingBlueprintEntity]) -> Optional[BuildingBlueprintRead]:
        if entity is None:
            return None
        
        try:
            # Check if entity is a dataclass and use asdict, or manually create dict
            if dataclasses.is_dataclass(entity):
                entity_dict_raw = dataclasses.asdict(entity)
            else:
                # Use the to_dict method or create a dict manually
                if hasattr(entity, 'to_dict'):
                    entity_dict_raw = entity.to_dict()
                else:
                    # Manual conversion
                    entity_dict_raw = {
                        'entity_id': entity.entity_id,
                        'name': entity.name,
                        'description': entity.description,
                        'theme_id': entity.theme_id,
                        'is_unique_per_settlement': entity.is_unique_per_settlement,
                        'metadata_': entity.metadata_,
                        'stages': [s.to_dict() if hasattr(s, 'to_dict') else vars(s) for s in entity.stages],
                        'created_at': entity.created_at,
                        'updated_at': entity.updated_at
                    }

            # Helper function to recursively rename 'entity_id' to 'id'
            def rename_entity_id_to_id_recursive(data: Any) -> Any:
                if isinstance(data, dict):
                    # Rename 'entity_id' to 'id'
                    if 'entity_id' in data and 'id' not in data:
                        data['id'] = data.pop('entity_id')
                    
                    # Handle _metadata alias specifically for the top-level blueprint dict
                    # This heuristic assumes only the top-level dict (representing BuildingBlueprintEntity)
                    # will have 'stages' as a direct key and also need metadata_ aliasing.
                    # Adjust if your structure is different or if stages/features also have metadata_ to alias.
                    if 'metadata_' in data and '_metadata' not in data and 'stages' in data: # Check for 'stages' to target blueprint
                        data['_metadata'] = data.pop('metadata_')

                    for key, value in data.items():
                        data[key] = rename_entity_id_to_id_recursive(value) # Recurse for values
                elif isinstance(data, list):
                    return [rename_entity_id_to_id_recursive(item) for item in data] # Recurse for list items
                return data

            entity_dict_processed = rename_entity_id_to_id_recursive(entity_dict_raw)
            
            # Ensure required fields exist
            if 'theme_id' not in entity_dict_processed and hasattr(entity, 'theme_id'):
                entity_dict_processed['theme_id'] = entity.theme_id
            
            if 'created_at' not in entity_dict_processed and hasattr(entity, 'created_at'):
                entity_dict_processed['created_at'] = entity.created_at
                
            if 'updated_at' not in entity_dict_processed and hasattr(entity, 'updated_at'):
                entity_dict_processed['updated_at'] = entity.updated_at
            
            # Convert datetime objects to ISO format strings for JSON serialization if needed
            if 'created_at' in entity_dict_processed and isinstance(entity_dict_processed['created_at'], datetime):
                entity_dict_processed['created_at'] = entity_dict_processed['created_at'].isoformat()
                
            if 'updated_at' in entity_dict_processed and isinstance(entity_dict_processed['updated_at'], datetime):
                entity_dict_processed['updated_at'] = entity_dict_processed['updated_at'].isoformat()
            
            return BuildingBlueprintRead.model_validate(entity_dict_processed)
            
        except Exception as e:
            # Log the processed dict if validation fails to see its structure
            logging.error(
                f"Failed to convert BuildingBlueprintEntity to Read schema. Error: {e}\n"
                f"Processed entity dict: {entity_dict_processed if 'entity_dict_processed' in locals() else 'entity_dict_raw was None or error before processing'}\n"
                f"Original entity data: {entity}",
                exc_info=True # This will include the full traceback for the pydantic error
            )
            raise ValueError("Internal error converting blueprint data.") # Re-raise a generic error

    async def create_blueprint(self, blueprint_data: BuildingBlueprintCreate) -> BuildingBlueprintRead:

        logging.info(f"Attempting to create blueprint: {blueprint_data.name}")
        existing_by_name = await self.repository.find_by_name(name=blueprint_data.name, theme_id=blueprint_data.theme_id)
        if existing_by_name:
             raise ValueError(f"Building blueprint with name '{blueprint_data.name}' already exists (for this theme).")
        if not blueprint_data.stages:
            raise ValueError("Building blueprint must have at least one stage.")

        transient_entity = self.manager.create_transient_blueprint(schema_data=blueprint_data)
        
        try:
            saved_entity = await self.repository.save_blueprint_with_stages(transient_entity)
        except Exception as e:
            logging.error(f"Database error saving blueprint '{blueprint_data.name}': {e}", exc_info=True)
            raise ValueError(f"Could not save building blueprint due to a database issue: {e}")

        read_schema = await self._convert_entity_to_read_schema(saved_entity)
        
        logging.info(f"Successfully created blueprint: {read_schema.name} (ID: {read_schema.id})")
        return read_schema

    async def get_blueprint(self, blueprint_id: uuid.UUID) -> Optional[BuildingBlueprintRead]:
        entity = await self.repository.find_by_id_with_details(blueprint_id)

        return await self._convert_entity_to_read_schema(entity)

    async def get_all_blueprints(self, skip: int = 0, limit: int = 100, theme_id: Optional[uuid.UUID] = None) -> List[BuildingBlueprintRead]:
        entities = await self.repository.find_all_with_details(skip=skip, limit=limit, theme_id=theme_id)
        read_schemas = []
        for entity in entities:
            read_schemas.append(await self._convert_entity_to_read_schema(entity))
        return read_schemas
    
    async def update_blueprint(self, blueprint_id: uuid.UUID, update_data: BuildingBlueprintUpdate) -> Optional[BuildingBlueprintRead]:
        logging.info(f"Attempting to update blueprint ID: {blueprint_id}")
        entity = await self.repository.find_by_id_with_details(blueprint_id)
        if not entity:
            return None

        update_dict = update_data.model_dump(exclude_unset=True, by_alias=True)
        
        updated_fields = False
        for key, value in update_dict.items():
            entity_key = key
            if key == "_metadata": entity_key = "metadata_"
            
            if hasattr(entity, entity_key) and getattr(entity, entity_key) != value:
                setattr(entity, entity_key, value)
                updated_fields = True
        
        if not updated_fields:
            logging.info(f"No changes detected for blueprint {blueprint_id}.")
            return await self._convert_entity_to_read_schema(entity)

        entity.updated_at = datetime.now(timezone.utc)

        try:
            saved_entity = await self.repository.save(entity)
        except Exception as e:
            logging.error(f"Database error updating blueprint '{entity.name}': {e}", exc_info=True)
            raise ValueError(f"Could not update blueprint: {e}")
            
        refetched_entity = await self.repository.find_by_id_with_details(saved_entity.entity_id)
        return await self._convert_entity_to_read_schema(refetched_entity)

    async def get_blueprint_entity(self, blueprint_id: uuid.UUID) -> Optional[BuildingBlueprintEntity]:
        """Returns the domain entity, not the read schema."""
        return await self.repository.find_by_id_with_details(blueprint_id)

    async def delete_blueprint(self, blueprint_id: uuid.UUID) -> bool:

        logging.info(f"Attempting to delete blueprint ID: {blueprint_id}")
        deleted = await self.repository.delete(blueprint_id)
        if deleted:
            logging.info(f"Successfully deleted blueprint: {blueprint_id}")
        else:
            logging.warning(f"Blueprint not found for deletion: {blueprint_id}")
        return deleted

# --- END OF FILE app/game_state/services/building_blueprint_service.py ---