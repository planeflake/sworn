# --- START OF FILE app/game_state/managers/building_blueprint_manager.py ---

import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from app.game_state.entities.building_blueprint import (
    BuildingBlueprintEntity,
    BlueprintStageEntity,
    BlueprintStageFeatureEntity
)
from app.game_state.managers.base_manager import BaseManager # Assuming you have a BaseManager
from app.api.schemas.building_blueprint_schema import ( # For type hinting if used
    BuildingBlueprintCreate,
    BlueprintStageCreate,
    BlueprintStageFeatureCreate
)


class BuildingBlueprintManager(BaseManager): # Inherit from BaseManager
    """
    Manager for BuildingBlueprint domain logic, primarily for creating transient entities
    from schema data.
    """

    @staticmethod
    def create_transient_feature(
        schema_data: BlueprintStageFeatureCreate, # Or pass individual fields
        parent_stage_id: uuid.UUID, # Transient ID for linking if needed before saving
        feature_id: Optional[uuid.UUID] = None
    ) -> BlueprintStageFeatureEntity:
        if feature_id is None:
            feature_id = uuid.uuid4() # Or let BaseManager handle it if creating one-by-one

        return BlueprintStageFeatureEntity(
            entity_id=feature_id,
            name=schema_data.name,
            blueprint_stage_id=parent_stage_id, # Important for relational context
            feature_key=schema_data.feature_key,
            description=schema_data.description,
            required_professions=schema_data.required_professions,
            additional_resource_costs=schema_data.additional_resource_costs,
            additional_duration_days=schema_data.additional_duration_days,
            effects=schema_data.effects,
            created_at=datetime.now(timezone.utc), # Set by entity default usually
            updated_at=datetime.now(timezone.utc)  # Set by entity default usually
        )

    @staticmethod
    def create_transient_stage(
        schema_data: BlueprintStageCreate, # Or pass individual fields
        parent_blueprint_id: uuid.UUID, # Transient ID for linking
        stage_id: Optional[uuid.UUID] = None
    ) -> BlueprintStageEntity:
        if stage_id is None:
            stage_id = uuid.uuid4()

        features = []
        # If creating nested features, assign a transient stage_id for now
        # The actual DB FK linking will happen during repository save
        transient_stage_link_id = stage_id # Use the generated/passed stage_id for child features

        for feature_schema in schema_data.optional_features:
            features.append(
                BuildingBlueprintManager.create_transient_feature(
                    feature_schema,
                    parent_stage_id=transient_stage_link_id # Link feature to this stage
                )
            )

        return BlueprintStageEntity(
            entity_id=stage_id,
            name=schema_data.name,
            building_blueprint_id=parent_blueprint_id, # Important for relational context
            stage_number=schema_data.stage_number,
            description=schema_data.description,
            duration_days=schema_data.duration_days,
            resource_costs=schema_data.resource_costs,
            profession_time_bonus=schema_data.profession_time_bonus,
            stage_completion_bonuses=schema_data.stage_completion_bonuses,
            optional_features=features,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @staticmethod
    def create_transient_blueprint(
        schema_data: BuildingBlueprintCreate, # Or pass individual fields
        blueprint_id: Optional[uuid.UUID] = None
    ) -> BuildingBlueprintEntity:
        """
        Creates a new transient (in-memory) BuildingBlueprintEntity with its stages and features.
        """
        if blueprint_id is None:
            blueprint_id = uuid.uuid4()

        stages = []
        # If creating nested stages, assign a transient blueprint_id for now
        transient_blueprint_link_id = blueprint_id # Use the generated/passed blueprint_id for child stages

        for stage_schema in schema_data.stages:
            stages.append(
                BuildingBlueprintManager.create_transient_stage(
                    stage_schema,
                    parent_blueprint_id=transient_blueprint_link_id # Link stage to this blueprint
                )
            )
        
        # Ensure stages are sorted by stage_number
        stages.sort(key=lambda s: s.stage_number)

        return BuildingBlueprintEntity(
            entity_id=blueprint_id,
            name=schema_data.name,
            description=schema_data.description,
            theme_id=schema_data.theme_id,
            is_unique_per_settlement=schema_data.is_unique_per_settlement,
            metadata_=schema_data.metadata_ if schema_data.metadata_ is not None else {},
            stages=stages,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

# --- END OF FILE app/game_state/managers/building_blueprint_manager.py ---