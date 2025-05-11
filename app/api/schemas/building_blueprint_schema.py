# --- START OF FILE app/game_state/schemas/building_blueprint_schema.py ---

import uuid
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# You might need to import enums or other types if they are used in _metadata or effects

# --- BlueprintStageFeature Schemas ---
class BlueprintStageFeatureBase(BaseModel):
    feature_key: str = Field(..., min_length=1, max_length=100, description="Unique key for this feature within the stage, e.g., 'arrow_slits'.")
    name: str = Field(..., min_length=1, max_length=150, description="User-facing name of the feature.")
    description: Optional[str] = Field(None, max_length=1000)
    required_professions: List[uuid.UUID] = Field(default_factory=list, description="List of profession IDs required for this feature.")
    additional_resource_costs: List[Dict[str, Any]] = Field(default_factory=list, description="E.g., [{'resource_id': UUID, 'amount': int}]")
    additional_duration_days: Optional[float] = Field(None, ge=0, description="Additional time in game days for this feature.")
    effects: Dict[str, Any] = Field(..., description="Game effects of this feature, e.g., {'stat_bonus': {'defense': 5}}.")

class BlueprintStageFeatureCreate(BlueprintStageFeatureBase):
    pass

class BlueprintStageFeatureRead(BlueprintStageFeatureBase):
    id: uuid.UUID
    blueprint_stage_id: uuid.UUID # Added for context when reading
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

# --- BlueprintStage Schemas ---
class BlueprintStageBase(BaseModel):
    stage_number: int = Field(..., ge=1, description="Sequential number of the stage in the blueprint.")
    name: str = Field(..., min_length=1, max_length=150, description="Name of the stage, e.g., 'Foundation'.")
    description: Optional[str] = Field(None, max_length=1000)
    duration_days: float = Field(..., ge=0, description="Base time in game days to complete this stage.")
    resource_costs: List[Dict[str, Any]] = Field(default_factory=list, description="E.g., [{'resource_id': UUID, 'amount': int}]")
    profession_time_bonus: List[Dict[str, Any]] = Field(default_factory=list, description="E.g., [{'profession_id': UUID, 'time_modifier': 0.1}] for 10% reduction.")
    stage_completion_bonuses: List[Dict[str, Any]] = Field(default_factory=list, description="Bonuses/abilities upon stage completion.")
    optional_features: List[BlueprintStageFeatureCreate] = Field(default_factory=list, description="Optional features available to build during this stage.")


class BlueprintStageCreate(BlueprintStageBase):
    pass # optional_features uses BlueprintStageFeatureCreate

class BlueprintStageRead(BlueprintStageBase):
    id: uuid.UUID
    building_blueprint_id: uuid.UUID # Added for context when reading
    optional_features: List[BlueprintStageFeatureRead] = Field(default_factory=list) # Read schema for features
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# --- BuildingBlueprint Schemas ---
class BuildingBlueprintBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Unique internal name/ID for the blueprint.")
    description: Optional[str] = Field(None, max_length=2000)
    theme_id: uuid.UUID = Field(..., description="ID of the Theme this blueprint belongs to.")
    is_unique_per_settlement: bool = Field(default=False, description="If true, only one instance of this blueprint can exist per settlement.")
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="_metadata", description="Overall blueprint metadata (e.g., final stats template, category).")
    # Note: 'stages' will be handled by specialized create/read schemas

class BuildingBlueprintCreate(BuildingBlueprintBase):
    stages: List[BlueprintStageCreate] = Field(..., min_length=1, description="List of construction stages for this blueprint.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "watchtower_mk1",
                    "description": "A standard wooden watchtower, offering basic defensive capabilities.",
                    "theme_id": str(uuid.uuid4()), # Replace with an actual theme_id from your system
                    "is_unique_per_settlement": False,
                    "_metadata": {
                        "category": "DEFENSIVE",
                        "final_base_hp": 150,
                        "max_garrison": 3,
                        "sight_range": 50
                    },
                    "stages": [
                        {
                            "stage_number": 1,
                            "name": "Lay Foundation",
                            "description": "Clear the ground and lay a sturdy stone foundation.",
                            "duration_days": 2.5,
                            "resource_costs": [{"resource_id": str(uuid.uuid4()), "amount": 50}, {"resource_id": str(uuid.uuid4()), "amount": 20}],
                            "profession_time_bonus": [{"profession_id": str(uuid.uuid4()), "time_modifier": 0.15}],
                            "stage_completion_bonuses": [{"bonus_type": "unlock_construction_option", "option_key": "wooden_scaffolding"}],
                            "optional_features": [
                                {
                                    "feature_key": "reinforced_foundation",
                                    "name": "Reinforced Foundation",
                                    "description": "Uses extra stone for a tougher base.",
                                    "required_professions": [str(uuid.uuid4())],
                                    "additional_resource_costs": [{"resource_id": str(uuid.uuid4()), "amount": 30}], # More stone
                                    "additional_duration_days": 1.0,
                                    "effects": {"building_stat_modifier": {"max_hp_add": 25}}
                                }
                            ]
                        },
                        {
                            "stage_number": 2,
                            "name": "Erect Walls & Lookout Post",
                            "description": "Build the main structure and the lookout platform.",
                            "duration_days": 5.0,
                            "resource_costs": [{"resource_id": str(uuid.uuid4()), "amount": 120}], # Wood
                            "profession_time_bonus": [],
                            "stage_completion_bonuses": [{"bonus_type": "stat_increase", "stat": "sight_range", "value": 20}],
                            "optional_features": [
                                {
                                    "feature_key": "arrow_slits",
                                    "name": "Arrow Slits",
                                    "description": "Provides better cover for archers.",
                                    "required_professions": [str(uuid.uuid4())], # Fletcher or Mason
                                    "additional_resource_costs": [],
                                    "effects": {"garrison_bonus": {"ranged_defense_mod": 0.1}}
                                },
                                {
                                    "feature_key": "signal_horn_post",
                                    "name": "Signal Horn Post",
                                    "description": "Allows guards to sound an alarm over a wider area.",
                                    "required_professions": [],
                                    "effects": {"building_ability": "wide_area_alert"}
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }


class BuildingBlueprintRead(BuildingBlueprintBase):
    id: uuid.UUID
    stages: List[BlueprintStageRead] = Field(default_factory=list) # Read schema for stages
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class BuildingBlueprintUpdate(BaseModel):
    """Schema for updating a building blueprint. Stages are not updated here directly."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    # theme_id: Optional[uuid.UUID] = None # Usually not changed, or done via a special operation
    is_unique_per_settlement: Optional[bool] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="_metadata")
    # Updating stages/features would likely be separate, more complex operations
    # e.g., add_stage, update_stage_feature, remove_feature, etc. via dedicated endpoints.

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "description": "An improved wooden watchtower, now with better sight range.",
                    "_metadata": {
                        "category": "DEFENSIVE",
                        "final_base_hp": 160, # Slightly increased
                        "max_garrison": 3,
                        "sight_range": 55 # Increased
                    }
                }
            ]
        }
    }

# --- END OF FILE app/game_state/schemas/building_blueprint_schema.py ---