# --- START OF FILE app/game_state/repositories/building_upgrade_blueprint_repository.py ---

from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.game_state.repositories.base_repository import BaseRepository
from app.db.models.building_upgrade_blueprint import BuildingUpgradeBlueprint
from app.game_state.entities.building.building_upgrade_blueprint_pydantic import BuildingUpgradeBlueprintEntityPydantic
from uuid import UUID
from typing import Optional

class BuildingUpgradeBlueprintRepository(
    BaseRepository[BuildingUpgradeBlueprintEntityPydantic, BuildingUpgradeBlueprint, UUID]
):
    """Repository for BuildingUpgradeBlueprint data operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(
            db=db,
            model_cls=BuildingUpgradeBlueprint,
            entity_cls=BuildingUpgradeBlueprintEntityPydantic
        )
        logging.info("BuildingUpgradeBlueprintRepository initialized.")

# --- END OF FILE app/game_state/repositories/building_upgrade_blueprint_repository.py ---
