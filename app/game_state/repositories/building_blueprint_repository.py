# --- START OF FILE app/game_state/repositories/building_blueprint_repository.py ---

import logging
import uuid
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload

from app.db.models.building_blueprint import BuildingBlueprint as BuildingBlueprintDB
from app.db.models.blueprint_stage import BlueprintStage as BlueprintStageDB # Assuming this path
from app.db.models.blueprint_stage_feature import BlueprintStageFeature as BlueprintStageFeatureDB # Assuming this path

from app.game_state.entities.building_blueprint import (
    BuildingBlueprintEntity,
    BlueprintStageEntity,
    BlueprintStageFeatureEntity
)
from app.game_state.repositories.base_repository import BaseRepository
import dataclasses # For converting entity to dict

class BuildingBlueprintRepository(BaseRepository[BuildingBlueprintEntity, BuildingBlueprintDB, uuid.UUID]):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model_cls=BuildingBlueprintDB, entity_cls=BuildingBlueprintEntity)
        logging.info(
            f"BuildingBlueprintRepository initialized with model: {self.model_cls.__name__} "
            f"and entity: {self.entity_cls.__name__}"
        )

    async def _convert_db_stages_to_entity_stages(self, db_stages: List[BlueprintStageDB]) -> List[BlueprintStageEntity]:
        entity_stages = []
        for db_stage in db_stages:
            entity_features = []
            if db_stage.optional_features: # Ensure features list exists and is not None
                for db_feature in db_stage.optional_features:
                    feature_data = {f.name: getattr(db_feature, f.name) for f in dataclasses.fields(BlueprintStageFeatureEntity) if hasattr(db_feature, f.name)}
                    feature_data['entity_id'] = db_feature.id # Map DB id to entity_id
                    # feature_data['name'] is already mapped by the loop if it's a dataclass field and exists on db_feature
                    entity_features.append(BlueprintStageFeatureEntity(**feature_data))
            
            stage_data = {f.name: getattr(db_stage, f.name) for f in dataclasses.fields(BlueprintStageEntity) if f.name != 'optional_features' and hasattr(db_stage, f.name)}
            stage_data['entity_id'] = db_stage.id
            stage_data['optional_features'] = entity_features
            entity_stages.append(BlueprintStageEntity(**stage_data))
        entity_stages.sort(key=lambda s: s.stage_number) # Ensure sorted
        return entity_stages

    async def _convert_to_entity(self, db_obj: BuildingBlueprintDB) -> Optional[BuildingBlueprintEntity]:
        """Overrides BaseRepository method to handle nested stages and features."""
        if db_obj is None:
            return None

        # Basic conversion for BuildingBlueprint fields (handled by BaseRepository's logic conceptually)
        # For this override, we do it manually to ensure deep conversion.
        blueprint_data = {}
        # Iterate entity fields to decide what to pull from db_obj
        for f in dataclasses.fields(self.entity_cls):
            if f.name == 'stages': # Handle stages separately
                continue
            if f.name == 'metadata_': # Handle alias
                 if hasattr(db_obj, '_metadata'):
                    blueprint_data[f.name] = getattr(db_obj, '_metadata')
                 continue

            if hasattr(db_obj, f.name):
                blueprint_data[f.name] = getattr(db_obj, f.name)
        
        blueprint_data['entity_id'] = db_obj.id # Ensure BaseEntity's entity_id is set from db_obj.id

        # Convert nested stages and their features
        if db_obj.stages:
            blueprint_data['stages'] = await self._convert_db_stages_to_entity_stages(db_obj.stages)
        else:
            blueprint_data['stages'] = []
        
        try:
            return self.entity_cls(**blueprint_data)
        except Exception as e:
            logging.error(f"Error instantiating BuildingBlueprintEntity from DB data: {e}", exc_info=True)
            logging.error(f"Data for instantiation: {blueprint_data}")
            return None


    async def _entity_to_model_dict(self, entity: BuildingBlueprintEntity, is_new: bool = False) -> Dict[str, Any]:
        """
        Converts domain entity (BuildingBlueprintEntity with nested stages/features)
        to a dictionary suitable for SQLAlchemy model instantiation or update.
        This needs careful handling for nested structures if creating new.
        For simplicity, this example assumes direct field mapping for the top-level blueprint.
        Saving nested stages/features is complex and usually handled by the service layer
        by creating DB model instances for stages/features and associating them.
        """
        entity_data = dataclasses.asdict(entity)
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
            if key in self._model_column_keys:
                model_data[key] = value
        
        if is_new and 'id' in model_data and 'id' in self._pk_server_default_names:
            model_data.pop('id', None) # Let DB generate ID if it's server-defaulted

        return model_data


    async def find_by_id_with_details(self, blueprint_id: uuid.UUID) -> Optional[BuildingBlueprintEntity]:
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

    async def find_all_with_details(self, skip: int = 0, limit: int = 100, theme_id: Optional[uuid.UUID] = None) -> List[BuildingBlueprintEntity]:
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

    async def find_by_name(self, name: str, theme_id: Optional[uuid.UUID] = None) -> Optional[BuildingBlueprintEntity]:
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


    async def save_blueprint_with_stages(self, blueprint_entity: BuildingBlueprintEntity) -> BuildingBlueprintEntity:
        """
        Saves a complete blueprint entity, including its stages and features.
        This is a complex operation that involves creating/updating multiple related DB objects.
        This method demonstrates a full replacement or creation strategy.
        More granular updates (add/remove stage/feature) would need separate methods.
        """
        # This is a simplified example. A robust implementation needs to handle:
        # 1. Existing blueprint? -> Update or error?
        # 2. Existing stages/features? -> Update, delete and recreate, or merge?
        # For creation of a NEW blueprint with all its parts:
        
        # Check if blueprint with this name and theme_id already exists if that's a constraint
        # existing_bp = await self.find_by_name(blueprint_entity.name, blueprint_entity.theme_id)
        # if existing_bp and (blueprint_entity.entity_id is None or existing_bp.entity_id != blueprint_entity.entity_id):
        #    raise ValueError(f"Blueprint with name '{blueprint_entity.name}' and theme '{blueprint_entity.theme_id}' already exists.")


        db_blueprint = None
        if blueprint_entity.entity_id: # Attempt to fetch if ID is provided (update scenario)
            db_blueprint = await self.db.get(BuildingBlueprintDB, blueprint_entity.entity_id, 
                                             options=[selectinload(BuildingBlueprintDB.stages)
                                                      .selectinload(BlueprintStageDB.optional_features)])

        if db_blueprint is None: # Create new blueprint
            blueprint_model_data = await self._entity_to_model_dict(blueprint_entity, is_new=True)
            # Pop relationship fields if they accidentally got into model_data
            blueprint_model_data.pop('stages', None)
            db_blueprint = BuildingBlueprintDB(**blueprint_model_data)
            self.db.add(db_blueprint)
            await self.db.flush() # Flush to get db_blueprint.id if it's new
        else: # Update existing blueprint's top-level fields
            update_data = await self._entity_to_model_dict(blueprint_entity, is_new=False)
            update_data.pop('id', None) # Don't update PK
            update_data.pop('stages', None)
            for key, value in update_data.items():
                setattr(db_blueprint, key, value)
        
        # --- Handle Stages and Features (Example: Delete and Recreate strategy for simplicity) ---
        # A more sophisticated approach would diff and update existing stages/features.
        
        # Clear existing stages for this blueprint if updating (delete-orphan cascade should handle features)
        if db_blueprint.stages:
            for stage_to_remove in list(db_blueprint.stages): # Iterate over a copy
                 await self.db.delete(stage_to_remove) # This will cascade to features due to delete-orphan
            await self.db.flush() # Ensure deletions are processed
            db_blueprint.stages.clear() # Clear the ORM collection

        # Create new stages and features from the entity
        for stage_entity in blueprint_entity.stages:
            db_stage = BlueprintStageDB(
                # id=stage_entity.entity_id, # If you want to control IDs from entity
                building_blueprint_id=db_blueprint.id, # Link to parent blueprint
                name=stage_entity.name,
                stage_number=stage_entity.stage_number,
                description=stage_entity.description,
                duration_days=stage_entity.duration_days,
                resource_costs=stage_entity.resource_costs,
                profession_time_bonus=stage_entity.profession_time_bonus,
                stage_completion_bonuses=stage_entity.stage_completion_bonuses
                # created_at, updated_at are server_default
            )
            # self.db.add(db_stage) # Adding via relationship below is often preferred

            for feature_entity in stage_entity.optional_features:
                db_feature = BlueprintStageFeatureDB(
                    # id=feature_entity.entity_id,
                    # blueprint_stage_id will be set by relationship
                    name=feature_entity.name,
                    feature_key=feature_entity.feature_key,
                    description=feature_entity.description,
                    required_professions=feature_entity.required_professions,
                    additional_resource_costs=feature_entity.additional_resource_costs,
                    additional_duration_days=feature_entity.additional_duration_days,
                    effects=feature_entity.effects
                )
                db_stage.optional_features.append(db_feature)
            db_blueprint.stages.append(db_stage) # This associates stage with blueprint AND adds to session if blueprint is already persistent

        await self.db.flush()
        await self.db.refresh(db_blueprint, attribute_names=['stages']) # Refresh to get all children
        for stage in db_blueprint.stages: # Refresh children's children
            await self.db.refresh(stage, attribute_names=['optional_features'])

        return await self._convert_to_entity(db_blueprint)

# --- END OF FILE app/game_state/repositories/building_blueprint_repository.py ---