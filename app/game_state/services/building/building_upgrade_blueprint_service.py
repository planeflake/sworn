# --- START OF FILE app/game_state/services/building_upgrade_blueprint_service.py ---

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional, Dict # Import Dict for type hint

from app.game_state.repositories.building_upgrade_blueprint_repository import BuildingUpgradeBlueprintRepository
from app.game_state.managers.building_upgrade_blueprint_manager import BuildingUpgradeBlueprintManager
from app.game_state.entities.building.building_upgrade_blueprint_pydantic import BuildingUpgradeBlueprintEntityPydantic
from app.api.schemas.building_upgrade_blueprint_schema import ( # Import API Schemas
    BuildingUpgradeBlueprintRead,
    BuildingUpgradeBlueprintCreate,
    BuildingUpgradeBlueprintUpdate,
)
# Optional: Import other services for validation (e.g., ResourceService, ProfessionDefinitionService)

class BuildingUpgradeBlueprintService:
    """Service layer for BuildingUpgradeBlueprint operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = BuildingUpgradeBlueprintRepository(db=self.db)
        self.manager = BuildingUpgradeBlueprintManager() # Instantiate manager

    async def _convert_entity_to_read_schema(
        self, entity: Optional[BuildingUpgradeBlueprintEntityPydantic]
    ) -> Optional[BuildingUpgradeBlueprintRead]:
        if entity is None:
            return None
        try:
            entity_dict = entity.to_dict()

            # Convert UUID keys in cost dicts to strings for the schema
            if 'resource_cost' in entity_dict and entity_dict['resource_cost'] is not None:
                entity_dict['resource_cost'] = {str(k): v for k, v in entity_dict['resource_cost'].items()}
            if 'profession_cost' in entity_dict and entity_dict['profession_cost'] is not None:
                entity_dict['profession_cost'] = {str(k): v for k, v in entity_dict['profession_cost'].items()}

            return BuildingUpgradeBlueprintRead.model_validate(entity_dict)
        except Exception as e:
            logging.error(f"Failed to convert BuildingUpgradeBlueprintEntity to Read schema: {e}", exc_info=True)
            raise ValueError("Internal error converting upgrade blueprint data.") from e

    async def create_upgrade_blueprint(
        self, data: BuildingUpgradeBlueprintCreate
    ) -> BuildingUpgradeBlueprintRead:
        """Creates a new building upgrade blueprint definition."""
        logging.info(f"Attempting to create upgrade blueprint: {data.name}")

        existing = await self.repository.find_by_name(data.name)
        if existing:
            raise ValueError(f"Upgrade blueprint with name '{data.name}' already exists.")

        # Convert string UUIDs from schema back to UUID objects for the entity/manager
        resource_cost_uuid_keys: Optional[Dict[UUID, int]] = None
        if data.resource_cost:
            try:
                resource_cost_uuid_keys = {UUID(k): v for k, v in data.resource_cost.items()}
            except ValueError as e:
                raise ValueError(f"Invalid UUID format in resource_cost keys: {e}")

        profession_cost_uuid_keys: Optional[Dict[UUID, int]] = None
        if data.profession_cost:
            try:
                profession_cost_uuid_keys = {UUID(k): v for k, v in data.profession_cost.items()}
            except ValueError as e:
                raise ValueError(f"Invalid UUID format in profession_cost keys: {e}")

        # Use the manager to create the transient domain entity
        transient_entity = self.manager.create(
            name=data.name,
            display_name=data.display_name,
            description=data.description,
            target_blueprint_criteria=data.target_blueprint_criteria,
            prerequisites=data.prerequisites,
            resource_cost=resource_cost_uuid_keys,
            profession_cost=profession_cost_uuid_keys,
            duration_days=data.duration_days,
            effects=data.effects,
            is_initial_choice=data.is_initial_choice,
        )

        try:
            saved_entity = await self.repository.save(transient_entity)
        except Exception as e:
            logging.error(f"DB error saving upgrade blueprint '{data.name}': {e}", exc_info=True)
            raise ValueError(f"Could not save upgrade blueprint: {e}") from e

        read_schema = await self._convert_entity_to_read_schema(saved_entity)
        if read_schema is None:
             logging.error(f"Saved upgrade bp {saved_entity.entity_id} but failed conversion.")
             raise ValueError("Internal error processing saved upgrade blueprint.")

        logging.info(f"Created upgrade blueprint: {read_schema.name} (ID: {read_schema.id})")
        return read_schema

    async def get_upgrade_blueprint(self, blueprint_id: UUID) -> Optional[BuildingUpgradeBlueprintRead]:
        entity = await self.repository.find_by_id(blueprint_id)
        return await self._convert_entity_to_read_schema(entity)

    async def get_all_upgrade_blueprints(self, skip: int = 0, limit: int = 100) -> List[BuildingUpgradeBlueprintRead]:
        entities = await self.repository.find_all(skip=skip, limit=limit)
        return [
            schema for entity in entities
            if (schema := await self._convert_entity_to_read_schema(entity)) is not None
        ]

    async def update_upgrade_blueprint(
        self, blueprint_id: UUID, update_data: BuildingUpgradeBlueprintUpdate
    ) -> Optional[BuildingUpgradeBlueprintRead]:
        # Handle UUID conversion for cost dictionaries before update
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Handle conversion for cost dicts if they are being updated
        if 'resource_cost' in update_dict and update_dict['resource_cost'] is not None:
            try:
                update_dict['resource_cost'] = {UUID(k): v for k, v in update_dict['resource_cost'].items()}
            except ValueError as e:
                raise ValueError(f"Invalid UUID format in resource_cost keys for update: {e}")
        if 'profession_cost' in update_dict and update_dict['profession_cost'] is not None:
            try:
                update_dict['profession_cost'] = {UUID(k): v for k, v in update_dict['profession_cost'].items()}
            except ValueError as e:
                raise ValueError(f"Invalid UUID format in profession_cost keys for update: {e}")

        # Use centralized update method from base repository
        try:
            updated_entity = await self.repository.update_entity(blueprint_id, update_dict)
            if updated_entity:
                return await self._convert_entity_to_read_schema(updated_entity)
            else:
                logging.warning(f"Building upgrade blueprint not found for update: {blueprint_id}")
                return None
        except Exception as e:
            logging.error(f"Database error updating upgrade blueprint ID {blueprint_id}: {e}", exc_info=True)
            raise ValueError(f"Could not update upgrade blueprint: {e}") from e

    async def delete_upgrade_blueprint(self, blueprint_id: UUID) -> bool:
        return await self.repository.delete(blueprint_id)

# --- END OF FILE app/game_state/services/building_upgrade_blueprint_service.py ---