# --- START OF FILE app/game_state/managers/building_upgrade_blueprint_manager.py ---

from app.game_state.entities.building.building_upgrade_blueprint_pydantic import BuildingUpgradeBlueprintEntityPydantic
from app.game_state.managers.base_manager import BaseManager
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid as uuid_module

class BuildingUpgradeBlueprintManager:
    """Manager for BuildingUpgradeBlueprint domain logic."""

    @staticmethod
    def create(
        name: str, # Unique internal key
        display_name: str,
        description: Optional[str] = None,
        target_blueprint_criteria: Optional[Dict[str, Any]] = None,
        prerequisites: Optional[Dict[str, Any]] = None,
        resource_cost: Optional[Dict[UUID, int]] = None,
        profession_cost: Optional[Dict[UUID, int]] = None,
        duration_days: int = 1,
        effects: Optional[Dict[str, Any]] = None,
        is_initial_choice: bool = False,
        entity_id: Optional[UUID] = None
    ) -> BuildingUpgradeBlueprintEntityPydantic:
        """Creates a new transient BuildingUpgradeBlueprintEntity."""

        entity_kwargs = {
            "display_name": display_name,
            "description": description,
            "target_blueprint_criteria": target_blueprint_criteria or {},
            "prerequisites": prerequisites or {},
            "resource_cost": resource_cost or {},
            "profession_cost": profession_cost or {},
            "duration_days": duration_days,
            "effects": effects or {},
            "is_initial_choice": is_initial_choice,
            "name": name, # For BaseEntity
        }

        upgrade_bp_entity = BaseManager.create(
            entity_class=BuildingUpgradeBlueprintEntityPydantic,
            entity_id=entity_id,
            **entity_kwargs
        )
        return upgrade_bp_entity

# --- END OF FILE app/game_state/managers/building_upgrade_blueprint_manager.py ---