# --- START OF FILE app/game_state/managers/building_instance_manager.py ---

import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from app.game_state.entities.building_instance import BuildingInstance as BuildingInstanceEntity, BuildingStatus
from app.game_state.managers.base_manager import BaseManager # Assuming you have a BaseManager

class BuildingInstanceManager(BaseManager):
    @staticmethod
    def create_transient_instance(
        name: str,
        building_blueprint_id: uuid.UUID,
        settlement_id: uuid.UUID,
        entity_id: Optional[uuid.UUID] = None,
        level: int = 1,
        status: BuildingStatus = BuildingStatus.UNDER_CONSTRUCTION,
        current_hp: int = 10,
        max_hp: int = 100,
        inhabitants_count: int = 0,
        workers_count: int = 0,
        construction_progress: float = 0.0,
        current_stage_number: int = 1,
        active_features: Optional[List[uuid.UUID]] = None,
        stored_resources: Optional[Dict[Any, int]] = None, # Allow Any for key initially
        assigned_workers_details: Optional[Dict[Any, int]] = None, # Allow Any for key initially
        instance_description: Optional[str] = None,
    ) -> BuildingInstanceEntity:
        if entity_id is None:
            entity_id = uuid.uuid4()

        # Convert UUID keys to strings for JSONB fields
        final_stored_resources = {str(k): v for k, v in stored_resources.items()} if stored_resources else {}
        final_assigned_workers_details = {str(k): v for k, v in assigned_workers_details.items()} if assigned_workers_details else {}


        entity_kwargs = {
            "entity_id": entity_id,
            "name": name,
            "building_blueprint_id": building_blueprint_id,
            "settlement_id": settlement_id,
            "level": level,
            "status": status,
            "current_hp": current_hp,
            "max_hp": max_hp,
            "inhabitants_count": inhabitants_count,
            "workers_count": workers_count,
            "construction_progress": construction_progress,
            "current_stage_number": current_stage_number,
            "active_features": active_features if active_features is not None else [],
            "stored_resources": final_stored_resources, # Use string-keyed version
            "assigned_workers_details": final_assigned_workers_details, # Use string-keyed version
            "instance_description": instance_description,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        return BuildingInstanceEntity(**entity_kwargs)
# --- END OF FILE app/game_state/managers/building_instance_manager.py ---