# --- START OF FILE app/game_state/managers/building_instance_manager.py ---

import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from app.game_state.entities.building_instance import BuildingInstance as BuildingInstanceEntity, BuildingStatus
from app.game_state.managers.base_manager import BaseManager # Assuming you have a BaseManager

class BuildingInstanceManager(BaseManager): # Inherit from BaseManager
    """
    Manager for BuildingInstance domain logic.
    Handles creation of transient entities and potentially complex state transitions.
    """

    @staticmethod
    def create_transient_instance(
        name: str,
        building_blueprint_id: uuid.UUID,
        settlement_id: uuid.UUID,
        entity_id: Optional[uuid.UUID] = None, # Allow pre-assigned ID
        level: int = 1,
        status: BuildingStatus = BuildingStatus.UNDER_CONSTRUCTION,
        current_hp: int = 10, # Default low HP for under construction
        max_hp: int = 100,    # Placeholder, service should set from blueprint
        inhabitants_count: int = 0,
        workers_count: int = 0,
        construction_progress: float = 0.0,
        current_stage_number: int = 1,
        active_features: Optional[List[uuid.UUID]] = None,
        stored_resources: Optional[Dict[uuid.UUID, int]] = None,
        assigned_workers_details: Optional[Dict[str, int]] = None,
        instance_description: Optional[str] = None,
        # Pass other fields from BuildingInstanceEntity as needed
    ) -> BuildingInstanceEntity:
        """
        Creates a new transient (in-memory) BuildingInstanceEntity.
        The BaseManager.create method would typically handle UUID generation if entity_id is None.
        """
        if entity_id is None:
            entity_id = uuid.uuid4() # Or let BaseManager handle it

        entity_kwargs = {
            "entity_id": entity_id, # For BaseEntity
            "name": name,           # For BaseEntity
            "building_blueprint_id": building_blueprint_id,
            "settlement_id": settlement_id,
            "level": level,
            "status": status,
            "current_hp": current_hp,
            "max_hp": max_hp,
            "inhabitants_count": inhabitants_count, # Make sure entity uses this name
            "workers_count": workers_count,         # Make sure entity uses this name
            "construction_progress": construction_progress,
            "current_stage_number": current_stage_number,
            "active_features": active_features if active_features is not None else [],
            "stored_resources": stored_resources if stored_resources is not None else {},
            "assigned_workers_details": assigned_workers_details if assigned_workers_details is not None else {}, # Make sure entity uses this name
            "instance_description": instance_description,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        # If BaseManager.create exists and is suitable:
        # return BaseManager.create(entity_class=BuildingInstanceEntity, id=entity_id, **entity_kwargs)
        
        # Direct instantiation if BaseManager.create is simple or not fully implemented:
        # Ensure your BuildingInstanceEntity constructor matches these kwargs or handles them.
        # The BuildingInstanceEntity provided inherits name and entity_id from BaseEntity.
        # So, these need to be passed such that BaseEntity receives them.
        # If BaseEntity takes id and name as first args:
        # building_entity = BuildingInstanceEntity(entity_id=entity_id, name=name, **other_kwargs_for_BuildingInstance)
        # Assuming BuildingInstanceEntity can take all these as kwargs and BaseEntity is handled:
        
        # Adapt this call based on how BaseEntity and BuildingInstanceEntity constructors are set up.
        # If BuildingInstanceEntity uses KW_ONLY for its own fields after BaseEntity fields:
        return BuildingInstanceEntity(**entity_kwargs)


    @staticmethod
    def advance_construction(instance: BuildingInstanceEntity, progress_made: float, time_elapsed_days: float) -> BuildingInstanceEntity:
        """
        Logic to advance construction. This is an example of domain logic.
        This might involve checking resources, worker effects, etc., which would
        typically be coordinated by a Service that has access to other repositories/services.
        """
        if instance.status != BuildingStatus.UNDER_CONSTRUCTION:
            logging.warning(f"Cannot advance construction for building {instance.entity_id} with status {instance.status}")
            return instance

        instance.construction_progress += progress_made
        instance.construction_progress = min(instance.construction_progress, 1.0) # Cap at 100%

        # More complex logic:
        # - Get current stage definition from Blueprint (Service would do this)
        # - Check if stage.duration_days is met
        # - If instance.construction_progress >= 1.0:
        #     Call a method to complete_stage(instance) -> handled by Service

        instance.updated_at = datetime.now(timezone.utc)
        logging.info(f"Advanced construction for building {instance.entity_id} to {instance.construction_progress*100:.2f}%")
        return instance

    # Other potential manager methods:
    # - apply_damage(instance, damage_amount)
    # - repair(instance, repair_amount)
    # - update_status(instance, new_status) - with validation
    # - assign_worker_to_instance(instance, character_id, role) -> this would be more of a service level op

# --- END OF FILE app/game_state/managers/building_instance_manager.py ---