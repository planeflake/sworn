# --- START OF FILE app/game_state/services/building_blueprint_service.py ---

import logging
import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.repositories.building_blueprint_repository import BuildingBlueprintRepository
from app.game_state.managers.building_blueprint_manager import BuildingBlueprintManager
from app.game_state.entities.building.building_blueprint_pydantic import BuildingBlueprintPydantic
from app.game_state.services.core.theme_service import ThemeService
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

        read_schema = BuildingBlueprintRead.model_validate(saved_entity.model_dump())
        
        logging.info(f"Successfully created blueprint: {read_schema.name} (ID: {read_schema.id})")
        return read_schema

    async def get_blueprint(self, blueprint_id: uuid.UUID) -> Optional[BuildingBlueprintRead]:

        entity = await self.repository.find_by_id_with_details(blueprint_id)
        entity_response = BuildingBlueprintRead.model_validate(entity.model_dump())

        return entity_response

    async def get_all_blueprints(self, skip: int = 0, limit: int = 100, theme_id: Optional[uuid.UUID] = None) -> List[BuildingBlueprintRead]:
        buildings = await self.repository.find_all_with_details(skip=skip, limit=limit, theme_id=theme_id)
        entity_response = [BuildingBlueprintRead.model_validate(building.model_dump()) for building in buildings]

        return entity_response
    
    async def update_blueprint(self, blueprint_id: uuid.UUID, update_data: BuildingBlueprintUpdate) -> Optional[BuildingBlueprintRead]:
        logging.info(f"Attempting to update blueprint ID: {blueprint_id}")
        
        # Use centralized update method from base repository
        try:
            updated_entity = await self.repository.update_entity(blueprint_id, update_data)
            if updated_entity:

                refetched_entity = await self.repository.find_by_id_with_details(updated_entity.entity_id)
                response_schema = BuildingBlueprintRead.model_validate(refetched_entity.model_dump())
                return response_schema
            else:
                logging.warning(f"Building blueprint not found for update: {blueprint_id}")
                return None
        except Exception as e:
            logging.error(f"Database error updating blueprint ID {blueprint_id}: {e}", exc_info=True)
            raise ValueError(f"Could not update blueprint: {e}") from e

    async def get_blueprint_entity(self, blueprint_id: uuid.UUID) -> Optional[BuildingBlueprintPydantic]:
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