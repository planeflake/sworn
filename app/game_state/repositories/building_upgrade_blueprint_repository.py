# --- START OF FILE app/game_state/repositories/building_upgrade_blueprint_repository.py ---

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import List, Optional, Dict, Any
import logging
import dataclasses # For asdict

from app.db.models.building_upgrade_blueprint import BuildingUpgradeBlueprint # SQLAlchemy Model
from app.game_state.entities.building_upgrade_blueprint_entity import BuildingUpgradeBlueprintEntity # Domain Entity
from app.game_state.repositories.base_repository import BaseRepository

class BuildingUpgradeBlueprintRepository(BaseRepository[BuildingUpgradeBlueprintEntity, BuildingUpgradeBlueprint, UUID]):
    """Repository for BuildingUpgradeBlueprint data operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model_cls=BuildingUpgradeBlueprint, entity_cls=BuildingUpgradeBlueprintEntity)
        logging.info("BuildingUpgradeBlueprintRepository initialized.")

    # Override conversion methods if specific handling for JSONB keys (str vs UUID) is needed
    async def _entity_to_model_dict(self, entity: BuildingUpgradeBlueprintEntity, is_new: bool = False) -> Dict[str, Any]:
        """
        Converts domain entity to a dictionary for SQLAlchemy model,
        handling UUID keys in JSONB fields.
        """
        model_data = await super()._entity_to_model_dict(entity, is_new) # Get base conversion

        if 'resource_cost' in model_data and model_data['resource_cost'] is not None:
            model_data['resource_cost'] = {
                str(k): v for k, v in model_data['resource_cost'].items()
            }
        if 'profession_cost' in model_data and model_data['profession_cost'] is not None:
            model_data['profession_cost'] = {
                str(k): v for k, v in model_data['profession_cost'].items()
            }
        return model_data

    async def _convert_to_entity(self, db_obj: BuildingUpgradeBlueprint) -> Optional[BuildingUpgradeBlueprintEntity]:
        """
        Converts a DB model instance to a domain entity, handling UUID keys in JSONB.
        """
        entity_args = {}
        # Use dataclasses.fields for the entity to know what to expect
        for f_info in dataclasses.fields(self.entity_cls):
            if hasattr(db_obj, f_info.name):
                 entity_args[f_info.name] = getattr(db_obj, f_info.name)
            # Handle entity_id from BaseEntity mapping to id in DB model
            elif f_info.name == 'entity_id' and hasattr(db_obj, 'id'):
                entity_args[f_info.name] = getattr(db_obj, 'id')


        if 'resource_cost' in entity_args and entity_args['resource_cost'] is not None:
            try:
                entity_args['resource_cost'] = {
                    UUID(k): v for k, v in entity_args['resource_cost'].items()
                }
            except Exception as e:
                logging.error(f"Error converting resource_cost keys to UUID for {db_obj.id}: {e}")
                entity_args['resource_cost'] = {} # Default or raise
        if 'profession_cost' in entity_args and entity_args['profession_cost'] is not None:
            try:
                entity_args['profession_cost'] = {
                    UUID(k): v for k, v in entity_args['profession_cost'].items()
                }
            except Exception as e:
                logging.error(f"Error converting profession_cost keys to UUID for {db_obj.id}: {e}")
                entity_args['profession_cost'] = {} # Default or raise

        # Make sure all required fields for BaseEntity are present if not directly mapped
        if 'entity_id' not in entity_args and hasattr(db_obj, 'id'):
            entity_args['entity_id'] = db_obj.id
        if 'name' not in entity_args and hasattr(db_obj, 'name'): # 'name' is used for the unique key
            entity_args['name'] = db_obj.name

        try:
            return self.entity_cls(**entity_args)
        except TypeError as e:
            logging.error(f"TypeError instantiating {self.entity_cls.__name__} from DB object {db_obj.id}: {e}", exc_info=True)
            logging.error(f"Args passed: {entity_args.keys()}")
            raise


    async def find_by_name(self, name: str) -> Optional[BuildingUpgradeBlueprintEntity]:
        """Finds an upgrade blueprint by its unique name."""
        stmt = select(self.model_cls).where(self.model_cls.name == name)
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return await self._convert_to_entity(db_obj)
        return None

# --- END OF FILE app/game_state/repositories/building_upgrade_blueprint_repository.py ---