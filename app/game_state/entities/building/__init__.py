"""Building entities module.

This module contains entities related to buildings, 
including blueprints, instances, and upgrades.
"""

from app.game_state.entities.building.building import BuildingEntity, Building
from app.game_state.entities.building.building_pydantic import BuildingEntityPydantic
from app.game_state.entities.building.building_blueprint import (
    BuildingBlueprintEntity,
    BlueprintStageEntity,
    BlueprintStageFeatureEntity
)
from app.game_state.entities.building.building_blueprint_pydantic import (
    BuildingBlueprintPydantic,
    BlueprintStagePydantic,
    BlueprintStageFeaturePydantic
)
from app.game_state.entities.building.building_instance import BuildingInstanceEntity, BuildingInstance
from app.game_state.entities.building.building_instance_pydantic import BuildingInstanceEntityPydantic
from app.game_state.entities.building.building_upgrade_blueprint import BuildingUpgradeBlueprintEntity
from app.game_state.entities.building.building_upgrade_blueprint_pydantic import BuildingUpgradeBlueprintEntityPydantic