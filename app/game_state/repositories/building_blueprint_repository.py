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
        db_blueprint_to_save: Optional[BuildingBlueprintDB] = None # Use a new variable name for clarity
        
        if blueprint_entity.entity_id: # UPDATE PATH
            logging.debug(f"Attempting to fetch existing blueprint for update: {blueprint_entity.entity_id}")
            db_blueprint_instance = await self.db.get( # Use a different var name to avoid confusion
                BuildingBlueprintDB,
                blueprint_entity.entity_id,
                options=[ 
                    selectinload(BuildingBlueprintDB.stages).selectinload(BlueprintStageDB.optional_features)
                ]
            )

            if db_blueprint_instance:
                logging.debug(f"Found existing blueprint {db_blueprint_instance.id} for update.")
                # Update top-level fields
                update_data = await self._entity_to_model_dict(blueprint_entity, is_new=False)
                update_data.pop('id', None); update_data.pop('stages', None)
                for key, value in update_data.items(): setattr(db_blueprint_instance, key, value)
                
                # Clear existing stages for "delete and recreate"
                if db_blueprint_instance.stages: 
                    logging.debug(f"Deleting {len(db_blueprint_instance.stages)} existing stages for update.")
                    for stage_to_remove in list(db_blueprint_instance.stages): await self.db.delete(stage_to_remove)
                    # A flush here is needed to execute the deletes before potentially re-adding
                    # items with the same natural keys (if stages had unique constraints beyond PK)
                    # or if new stages might conflict.
                    await self.db.flush()
                    db_blueprint_instance.stages.clear() # Clear Python collection
                
                db_blueprint_to_save = db_blueprint_instance # This is the object we'll add new stages to
            else:
                logging.warning(f"Blueprint with ID {blueprint_entity.entity_id} for update not found. Will create as new.")
                # Falls through, db_blueprint_to_save will be None, triggering create logic

        if db_blueprint_to_save is None:  # CREATE new blueprint path
            logging.debug(f"Creating new blueprint: {blueprint_entity.name}")
            blueprint_model_data = await self._entity_to_model_dict(blueprint_entity, is_new=True)
            blueprint_model_data.pop('stages', None) # Remove stages data from parent dict
            
            # Create the parent DB object, but DON'T add stages to it yet via kwargs
            db_blueprint_to_save = BuildingBlueprintDB(**blueprint_model_data)
            self.db.add(db_blueprint_to_save) # Add parent to session
            # DO NOT FLUSH YET. Let's build the whole graph in Python first.

        # --- Construct the new stages and features as Python objects ---
        # These will be associated with db_blueprint_to_save.
        # The db_blueprint_to_save object is now either a new transient object added to the session,
        # or an existing persistent object whose stages collection was cleared.

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
                # building_blueprint_id will be set by relationship assignment/cascade
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
                    # blueprint_stage_id will be set by relationship assignment/cascade
                )
                new_features_for_stage.append(db_feature)
            db_stage_obj.optional_features = new_features_for_stage # Assign features to this stage
            
            new_stages_for_blueprint.append(db_stage_obj)

        # Now, assign the fully constructed list of new stages (with their features)
        # to the parent blueprint. This leverages SQLAlchemy's collection management and cascades.
        db_blueprint_to_save.stages = new_stages_for_blueprint
        
        logging.debug(f"All stages and features prepared for blueprint {getattr(db_blueprint_to_save, 'id', 'NEW')}. Flushing session...")
        await self.db.flush() # Persist parent (if new), all new stages, all new features, and updates to parent.
                              # This single flush should handle the entire object graph due to cascades.

        logging.debug(f"Refresh blueprint {db_blueprint_to_save.id} and its children post-save.")
        await self.db.refresh(db_blueprint_to_save, attribute_names=['theme', 'stages'])
        
        if db_blueprint_to_save.stages:
            for stage in db_blueprint_to_save.stages:
                await self.db.refresh(stage, attribute_names=['optional_features'])
        else:
            logging.debug(f"No stages found for blueprint {db_blueprint_to_save.id} after refresh.")

        return await self._convert_to_entity(db_blueprint_to_save)