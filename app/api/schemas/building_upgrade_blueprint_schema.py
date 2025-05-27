# --- START OF FILE app/api/schemas/building_upgrade_blueprint_schema.py ---

import uuid
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class BuildingUpgradeBlueprintBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150, description="Unique internal key for the upgrade.")
    display_name: str = Field(..., min_length=1, max_length=150, description="User-facing name.")
    description: Optional[str] = None
    target_blueprint_criteria: Dict[str, Any] = Field(default_factory=dict, description="Criteria for applicable base buildings.")
    prerequisites: Dict[str, Any] = Field(default_factory=dict, description="Prerequisites for applying the upgrade.")
    resource_cost: Dict[str, int] = Field(default_factory=dict, description="Resource costs (resource_uuid_str: count).") # Keys are UUID strings
    profession_cost: Dict[str, int] = Field(default_factory=dict, description="Profession costs (profession_def_uuid_str: count).") # Keys are UUID strings
    duration_days: int = Field(1, gt=0)
    effects: Dict[str, Any] = Field(default_factory=dict, description="Effects of the upgrade.")
    is_initial_choice: bool = False

class BuildingUpgradeBlueprintCreate(BuildingUpgradeBlueprintBase):
    pass

class BuildingUpgradeBlueprintUpdate(BaseModel): # Allow partial updates
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    display_name: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    target_blueprint_criteria: Optional[Dict[str, Any]] = None
    prerequisites: Optional[Dict[str, Any]] = None
    resource_cost: Optional[Dict[str, int]] = None
    profession_cost: Optional[Dict[str, int]] = None
    duration_days: Optional[int] = Field(None, gt=0)
    effects: Optional[Dict[str, Any]] = None
    is_initial_choice: Optional[bool] = None

class BuildingUpgradeBlueprintRead(BuildingUpgradeBlueprintBase):
    id: uuid.UUID # From BaseEntity's entity_id
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# --- END OF FILE app/api/schemas/building_upgrade_blueprint_schema.py ---