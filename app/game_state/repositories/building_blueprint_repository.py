# --- START OF FILE app/game_state/repositories/building_blueprint_repository.py ---

import logging
import uuid
from typing import List, Optional, Dict, Any, cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.models.building_blueprint import BuildingBlueprint as BuildingBlueprintDB
from app.db.models.blueprint_stage import BlueprintStage as BlueprintStageDB
from app.db.models.blueprint_stage_feature import BlueprintStageFeature as BlueprintStageFeatureDB # Assuming this path

from app.game_state.entities.building.building_blueprint_pydantic import (
    BuildingBlueprintPydantic
)
from app.game_state.repositories.base_repository import BaseRepository

class BuildingBlueprintRepository(BaseRepository[BuildingBlueprintPydantic, BuildingBlueprintDB, uuid.UUID]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model_cls=BuildingBlueprintDB, entity_cls=BuildingBlueprintPydantic)
        logging.info(
            f"BuildingBlueprintRepository initialized with model: {self.model_cls.__name__} "
            f"and entity: {self.entity_cls.__name__}"
        )

    async def _entity_to_model_dict(self, entity: BuildingBlueprintPydantic, is_new: bool = False) -> Dict[str, Any]:
        """
        Converts domain entity (BuildingBlueprintEntity with nested stages/features)
        to a dictionary suitable for SQLAlchemy model instantiation or update.
        This needs careful handling for nested structures if creating new.
        For simplicity, this example assumes direct field mapping for the top-level blueprint.
        Saving nested stages/features is complex and usually handled by the service layer
        by creating DB model instances for stages/features and associating them.
        """
        import datetime
        
        entity_data = entity.to_dict()
        model_data = {}

        for key, value in entity_data.items():
            if key == 'entity_id' and 'id' not in self._model_column_keys: # Map entity_id to id if model uses 'id'
                if 'id' in self._model_column_keys: model_data['id'] = value
                continue
            if key == 'stages': # Stages are relationships, not direct columns for the dict
                continue
            if key == 'metadata_': # Handle alias
                 if '_metadata' in self._model_column_keys:
                    model_data['_metadata'] = value
                 continue
            # Convert ISO format timestamp strings back to datetime objects
            if key in ['created_at', 'updated_at'] and isinstance(value, str):
                try:
                    # Parse ISO format string into datetime object with timezone
                    model_data[key] = datetime.datetime.fromisoformat(value)
                except (ValueError, TypeError):
                    # If parsing fails, use current time
                    model_data[key] = datetime.datetime.now(datetime.timezone.utc) if 'created_at' == key else None
                continue
            if key in self._model_column_keys:
                model_data[key] = value
        
        if is_new and 'id' in model_data and 'id' in self._pk_server_default_names:
            model_data.pop('id', None) # Let DB generate ID if it's server-defaulted

        return model_data

    async def find_by_id_with_details(self, blueprint_id: uuid.UUID) -> Optional[BuildingBlueprintPydantic]:
        """Finds a blueprint by ID and eagerly loads its stages and their features."""
        stmt = (
            select(self.model_cls)
            .where(self.model_cls.id == blueprint_id)
            .options(
                selectinload(self.model_cls.stages).selectinload(BlueprintStageDB.optional_features),
                selectinload(self.model_cls.theme) # Eager load theme
            )
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        return await self._convert_to_entity(db_obj) if db_obj else None

    async def find_all_with_details(self, skip: int = 0, limit: int = 100, theme_id: Optional[uuid.UUID] = None) -> List[BuildingBlueprintPydantic]:
        """Finds all blueprints, optionally filtered by theme, with details."""
        stmt = (
            select(self.model_cls)
            .options(
                selectinload(self.model_cls.stages).selectinload(BlueprintStageDB.optional_features),
                selectinload(self.model_cls.theme)
            )
            .order_by(self.model_cls.name) # Example ordering
            .offset(skip)
            .limit(limit)
        )
        if theme_id:
            stmt = stmt.where(self.model_cls.theme_id == theme_id)

        result = await self.db.execute(stmt)
        db_objs = result.scalars().all()
        entities = [await self._convert_to_entity(db_obj) for db_obj in db_objs]
        return [entity for entity in entities if entity is not None]

    async def find_by_name(self, name: str, theme_id: Optional[uuid.UUID] = None) -> Optional[BuildingBlueprintPydantic]:
        """Finds a blueprint by its unique name, optionally within a theme."""
        stmt = select(self.model_cls).where(self.model_cls.name == name)
        if theme_id:
            stmt = stmt.where(self.model_cls.theme_id == theme_id)
        
        stmt = stmt.options(
            selectinload(self.model_cls.stages).selectinload(BlueprintStageDB.optional_features)
        )
        result = await self.db.execute(stmt)
        db_obj = result.scalar_one_or_none()
        return await self._convert_to_entity(db_obj)

    async def save_blueprint_with_stages(self, blueprint_entity: BuildingBlueprintPydantic) -> BuildingBlueprintPydantic:
        db_blueprint_to_save: Optional[BuildingBlueprintDB] = None

        if blueprint_entity.entity_id:  # UPDATE PATH
            logging.debug(f"Attempting to fetch existing blueprint for update: {blueprint_entity.entity_id}")
            db_blueprint_instance: Optional[BuildingBlueprintDB] = await self.db.get(
                BuildingBlueprintDB,
                blueprint_entity.entity_id,
                options=[
                    selectinload(BuildingBlueprintDB.stages).selectinload(BlueprintStageDB.optional_features)
                ]
            )

            if db_blueprint_instance is not None:
                logging.debug(f"Found existing blueprint {db_blueprint_instance.id} for update.")
                # Update top-level fields
                update_data = await self._entity_to_model_dict(blueprint_entity, is_new=False)
                update_data.pop('id', None); update_data.pop('stages', None)
                for key, value in update_data.items(): setattr(db_blueprint_instance, key, value)

                # Clear existing stages for "delete and recreate"
                if db_blueprint_instance.stages:
                    # Since stages is just a Python list (Mapped[List["BlueprintStage"]]),
                    # we can work with it directly
                    stages_to_delete = list(db_blueprint_instance.stages)  # Create a copy of the list to iterate
                    logging.debug(f"Deleting {len(stages_to_delete)} existing stages")
                    for stage_to_remove in stages_to_delete:
                        await self.db.delete(stage_to_remove)

                    await self.db.flush()
                    # Since it's a list, we can just assign an empty list to clear it
                    db_blueprint_instance.stages = []

                db_blueprint_to_save = cast(BuildingBlueprintDB, db_blueprint_instance)
            else:
                logging.warning(f"Blueprint with ID {blueprint_entity.entity_id} for update not found. Will create as new.")

        if db_blueprint_to_save is None:  # CREATE new blueprint path
            logging.debug(f"Creating new blueprint: {blueprint_entity.name}")
            blueprint_model_data = await self._entity_to_model_dict(blueprint_entity, is_new=True)
            blueprint_model_data.pop('stages', None)  # Remove stages data from parent dict

            db_blueprint_to_save = BuildingBlueprintDB(**blueprint_model_data)
            self.db.add(db_blueprint_to_save)

        # Construct new stages and features
        new_stages_for_blueprint = []
        for stage_entity in blueprint_entity.stages:
            db_stage_obj = BlueprintStageDB(
                name=stage_entity.name,
                stage_number=stage_entity.stage_number,
                description=stage_entity.description,
                duration_days=stage_entity.duration_days,
                resource_costs=stage_entity.resource_costs,
                profession_time_bonus=stage_entity.profession_time_bonus,
                stage_completion_bonuses=stage_entity.stage_completion_bonuses,
            )

            new_features_for_stage = []
            for feature_entity in stage_entity.optional_features:
                db_feature = BlueprintStageFeatureDB(
                    name=feature_entity.name,
                    feature_key=feature_entity.feature_key,
                    description=feature_entity.description,
                    required_professions=feature_entity.required_professions,
                    additional_resource_costs=feature_entity.additional_resource_costs,
                    additional_duration_days=feature_entity.additional_duration_days,
                    effects=feature_entity.effects,
                )
                new_features_for_stage.append(db_feature)
            db_stage_obj.optional_features = new_features_for_stage

            new_stages_for_blueprint.append(db_stage_obj)

        # Assign new stages to the blueprint
        db_blueprint_to_save.stages = new_stages_for_blueprint

        logging.debug(f"All stages and features prepared for blueprint {getattr(db_blueprint_to_save, 'id', 'NEW')}. Flushing session...")
        await self.db.flush()

        logging.debug(f"Refresh blueprint {db_blueprint_to_save.id} and its children post-save.")
        await self.db.refresh(db_blueprint_to_save, attribute_names=['theme', 'stages'])

        # Check stages after refresh
        if db_blueprint_to_save.stages:
            # Since stages is a List, we can iterate it directly
            for stage in db_blueprint_to_save.stages:
                await self.db.refresh(stage, attribute_names=['optional_features'])
        else:
            logging.debug(f"No stages found for blueprint {db_blueprint_to_save.id} after refresh.")

        return await self._convert_to_entity(db_blueprint_to_save)