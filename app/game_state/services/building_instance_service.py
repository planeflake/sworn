# --- START OF FILE app/game_state/services/building_instance_service.py ---

import logging
import uuid
from typing import List, Optional, Tuple
import dataclasses
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.game_state.repositories.building_instance_repository import BuildingInstanceRepository
from app.game_state.managers.building_instance_manager import BuildingInstanceManager
from app.game_state.entities.building_instance import BuildingInstance as BuildingInstanceEntity, BuildingStatus
from app.api.schemas.building_instance import (
    BuildingInstanceRead,
    BuildingInstanceCreate,
    BuildingInstanceUpdate,
)
# Import other services/repositories needed for validation or fetching related data
# from app.game_state.services.settlement_service import SettlementService
# from app.game_state.repositories.building_blueprint_repository import BuildingBlueprintRepository
# from app.game_state.entities.building_blueprint import BuildingBlueprintEntity # If needed

class BuildingInstanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = BuildingInstanceRepository(db=self.db)
        self.manager = BuildingInstanceManager() # Instantiate manager
        # self.settlement_service = SettlementService(db=db) # Example
        # self.blueprint_repo = BuildingBlueprintRepository(db=db) # Example

    async def _convert_entity_to_read_schema(self, entity: Optional[BuildingInstanceEntity]) -> Optional[BuildingInstanceRead]:
        if entity is None:
            return None
        try:
            # Ensure entity_id is mapped to 'id' for the schema
            entity_dict = dataclasses.asdict(entity)
            if 'entity_id' in entity_dict and 'id' not in entity_dict:
                entity_dict['id'] = entity_dict.pop('entity_id')
            return BuildingInstanceRead.model_validate(entity_dict)
        except Exception as e:
            logging.error(f"Failed to convert BuildingInstanceEntity to Read schema: {e}", exc_info=True)
            raise ValueError("Internal error converting building instance data.")

    async def create_building_instance(self, creation_data: BuildingInstanceCreate) -> BuildingInstanceRead:
        logging.info(f"Attempting to create building instance: {creation_data.name} in settlement {creation_data.settlement_id}")

        # --- Validation ---
        # 1. Check if settlement exists
        # settlement = await self.settlement_service.get_settlement_entity(creation_data.settlement_id)
        # if not settlement:
        #     raise ValueError(f"Settlement with ID {creation_data.settlement_id} not found.")

        # 2. Check if blueprint exists
        # blueprint = await self.blueprint_repo.find_by_id(creation_data.building_blueprint_id)
        # if not blueprint:
        #     raise ValueError(f"BuildingBlueprint with ID {creation_data.building_blueprint_id} not found.")
        
        # 3. Check for uniqueness if blueprint.is_unique_per_settlement is True
        # existing_unique = await self.repository.find_by_settlement_and_blueprint(creation_data.settlement_id, creation_data.building_blueprint_id)
        # if blueprint.is_unique_per_settlement and existing_unique:
        #    raise ValueError(f"A '{blueprint.name}' already exists in settlement {creation_data.settlement_id} and is unique.")

        # --- Initial Values from Blueprint (Example) ---
        # initial_max_hp = blueprint.metadata.get("initial_max_hp", 100) # Fetch from blueprint
        # initial_current_hp = blueprint.metadata.get("initial_current_hp", 10) # If starting damaged or under construction
        initial_max_hp = creation_data.max_hp # Or take from creation_data if allowed
        initial_current_hp = creation_data.current_hp

        transient_entity = self.manager.create_transient_instance(
            name=creation_data.name,
            building_blueprint_id=creation_data.building_blueprint_id,
            settlement_id=creation_data.settlement_id,
            level=creation_data.level,
            status=creation_data.status, # Should likely be UNDER_CONSTRUCTION initially
            current_hp=initial_current_hp,
            max_hp=initial_max_hp,
            inhabitants_count=creation_data.inhabitants_count,
            workers_count=creation_data.workers_count,
            construction_progress=creation_data.construction_progress, # Should be 0.0
            current_stage_number=creation_data.current_stage_number, # Should be 1 (or 0)
            active_features=creation_data.active_features,
            stored_resources=creation_data.stored_resources,
            assigned_workers_details=creation_data.assigned_workers_details,
            instance_description=creation_data.instance_description,
        )
        
        # Ensure status is appropriate for initial creation
        if transient_entity.construction_progress < 1.0 and transient_entity.current_stage_number > 0: # Assuming stage 0 is "plot"
            transient_entity.status = BuildingStatus.UNDER_CONSTRUCTION
        elif transient_entity.construction_progress >= 1.0 and transient_entity.status == BuildingStatus.UNDER_CONSTRUCTION:
            transient_entity.status = BuildingStatus.ACTIVE # If somehow created fully built

        try:
            saved_entity = await self.repository.save(transient_entity)
        except Exception as e:
            logging.error(f"Database error saving building instance '{creation_data.name}': {e}", exc_info=True)
            raise ValueError(f"Could not save building instance: {e}")

        read_schema = await self._convert_entity_to_read_schema(saved_entity)
        if read_schema is None:
            raise ValueError("Internal error processing saved building instance data.")
        
        logging.info(f"Successfully created building instance: {read_schema.name} (ID: {read_schema.id})")
        return read_schema

    async def get_building_instance(self, instance_id: uuid.UUID) -> Optional[BuildingInstanceRead]:
        # entity = await self.repository.find_by_id(instance_id) # Simple find
        entity = await self.repository.get_instance_with_details(instance_id) # With eager loading
        return await self._convert_entity_to_read_schema(entity)

    async def list_buildings_in_settlement(self, settlement_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[BuildingInstanceRead]:
        # Add validation: check if settlement exists
        # settlement = await self.settlement_service.get_settlement_entity(settlement_id)
        # if not settlement:
        #     raise ValueError(f"Settlement with ID {settlement_id} not found.")
            
        entities = await self.repository.find_by_settlement_id(settlement_id=settlement_id, skip=skip, limit=limit)
        return [schema for entity in entities if (schema := await self._convert_entity_to_read_schema(entity)) is not None]

    async def update_building_instance(self, instance_id: uuid.UUID, update_data: BuildingInstanceUpdate) -> Optional[BuildingInstanceRead]:
        entity = await self.repository.find_by_id(instance_id)
        if not entity:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        updated_fields = False
        for key, value in update_dict.items():
            if hasattr(entity, key) and getattr(entity, key) != value:
                setattr(entity, key, value)
                updated_fields = True
        
        if not updated_fields:
            logging.info(f"No changes detected for building instance {instance_id}.")
            return await self._convert_entity_to_read_schema(entity)

        entity.updated_at = datetime.now(timezone.utc) # Manually update timestamp

        try:
            saved_entity = await self.repository.save(entity)
        except Exception as e:
            logging.error(f"Database error updating building instance '{entity.name}': {e}", exc_info=True)
            raise ValueError(f"Could not update building instance: {e}")
            
        return await self._convert_entity_to_read_schema(saved_entity)

    async def delete_building_instance(self, instance_id: uuid.UUID) -> bool:
        # Add checks: e.g., are there inhabitants? Ongoing processes?
        deleted = await self.repository.delete(instance_id)
        if deleted:
            logging.info(f"Successfully deleted building instance: {instance_id}")
        else:
            logging.warning(f"Building instance not found for deletion: {instance_id}")
        return deleted

    # --- More complex service methods ---
    async def advance_stage_construction(self, instance_id: uuid.UUID, progress_delta: float) -> BuildingInstanceRead:
        """
        Advances construction for the current stage of a building.
        If stage completes, moves to next stage or completes building.
        """
        instance = await self.repository.find_by_id(instance_id)
        if not instance:
            raise ValueError(f"Building instance {instance_id} not found.")
        if instance.status != BuildingStatus.UNDER_CONSTRUCTION:
            raise ValueError(f"Building {instance.name} is not under construction.")

        # Get blueprint and current stage definition (pseudo-code)
        # blueprint = await self.blueprint_repo.find_by_id(instance.building_blueprint_id)
        # if not blueprint:
        #     raise ValueError("Blueprint not found for building instance.")
        # current_stage_def = next((s for s in blueprint.stages if s.stage_number == instance.current_stage_number), None)
        # if not current_stage_def:
        #     raise ValueError(f"Stage {instance.current_stage_number} not found in blueprint.")

        instance.construction_progress += progress_delta
        instance.construction_progress = min(1.0, instance.construction_progress) # Cap at 100%

        if instance.construction_progress >= 1.0:
            # Stage complete!
            logging.info(f"Stage {instance.current_stage_number} for building {instance.name} (ID: {instance.entity_id}) complete.")
            # Apply stage completion bonuses, activate features from this stage etc.
            
            # Try to move to next stage
            # next_stage_number = instance.current_stage_number + 1
            # next_stage_def = next((s for s in blueprint.stages if s.stage_number == next_stage_number), None)
            
            # if next_stage_def:
            #     instance.current_stage_number = next_stage_number
            #     instance.construction_progress = 0.0
            #     logging.info(f"Building {instance.name} moving to stage {next_stage_number}.")
            # else:
            #     # All stages complete
            instance.status = BuildingStatus.ACTIVE
            #     instance.current_stage_number = 0 # Or a "completed" sentinel value
            #     instance.construction_progress = 1.0 # Ensure it's marked as fully done
            #     # Set final max_hp, max_inhabitants from blueprint._metadata
            #     logging.info(f"Building {instance.name} construction fully completed.")
        
        instance.updated_at = datetime.now(timezone.utc)
        saved_instance = await self.repository.save(instance)
        return await self._convert_entity_to_read_schema(saved_instance)

# --- END OF FILE app/game_state/services/building_instance_service.py ---