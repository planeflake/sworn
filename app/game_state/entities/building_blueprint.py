# --- START OF FILE app/game_state/entities/building_blueprint.py ---

import uuid
from dataclasses import dataclass, field, KW_ONLY
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Set

from .base import BaseEntity # Assuming app.game_state.entities.base.BaseEntity

@dataclass
class BlueprintStageFeatureEntity(BaseEntity): # Inherits entity_id, name
    """Domain Entity for an optional feature within a blueprint stage."""
    # entity_id: uuid.UUID (Inherited) - Represents this specific feature definition's ID
    # name: str (Inherited) - User-facing name of the feature

    _: KW_ONLY
    blueprint_stage_id: uuid.UUID # FK to the parent BlueprintStageEntity
    feature_key: str # Unique key within the stage, e.g., "arrow_slits"
    description: Optional[str] = None
    required_professions: List[uuid.UUID] = field(default_factory=list)
    additional_resource_costs: List[Dict[str, Any]] = field(default_factory=list) # [{'resource_id': UUID, 'amount': int}]
    additional_duration_days: Optional[float] = None
    effects: Dict[str, Any] = field(default_factory=dict)
    # created_at, updated_at if not in BaseEntity or need specific handling
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BlueprintStageEntity(BaseEntity): # Inherits entity_id, name
    """Domain Entity for a stage within a building blueprint."""
    # entity_id: uuid.UUID (Inherited) - Represents this specific stage definition's ID
    # name: str (Inherited) - Name of the stage, e.g., "Foundation"

    _: KW_ONLY
    building_blueprint_id: uuid.UUID # FK to the parent BuildingBlueprintEntity
    stage_number: int
    description: Optional[str] = None
    duration_days: float = 0.0
    resource_costs: List[Dict[str, Any]] = field(default_factory=list) # [{'resource_id': UUID, 'amount': int}]
    profession_time_bonus: List[Dict[str, Any]] = field(default_factory=list) # [{'profession_id': UUID, 'modifier': float}]
    stage_completion_bonuses: List[Dict[str, Any]] = field(default_factory=list)
    optional_features: List[BlueprintStageFeatureEntity] = field(default_factory=list) # Nested entities
    # created_at, updated_at if not in BaseEntity or need specific handling
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BuildingBlueprintEntity(BaseEntity): # Inherits entity_id, name
    """Domain Entity for a building blueprint definition."""
    # entity_id: uuid.UUID (Inherited) - Represents this blueprint definition's ID
    # name: str (Inherited) - Unique internal name/key for the blueprint

    _: KW_ONLY
    # display_name: str # If you want a separate display name from the internal 'name'
    description: Optional[str] = None
    theme_id: uuid.UUID
    is_unique_per_settlement: bool = False
    metadata_: Optional[Dict[str, Any]] = field(default_factory=dict) # Alias for _metadata
    stages: List[BlueprintStageEntity] = field(default_factory=list) # Nested entities
    # created_at, updated_at if not in BaseEntity or need specific handling
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if hasattr(super(), '__post_init__'):
            super().__post_init__() # type: ignore
        # Sort stages by stage_number if they are provided out of order
        if self.stages:
            self.stages.sort(key=lambda s: s.stage_number)
            
        # Initialize metadata if needed
        if self.metadata_ is None:
            self.metadata_ = {}
            
        # Ensure attributes list exists in metadata
        if 'attributes' not in self.metadata_:
            self.metadata_['attributes'] = []
            
    def get_attributes(self) -> List[str]:
        """
        Get the building's attributes from metadata.
        Returns a list of attribute string values.
        """
        if not self.metadata_ or 'attributes' not in self.metadata_:
            return []
        return self.metadata_.get('attributes', [])
    
    def has_attribute(self, attribute_value: str) -> bool:
        """
        Check if the building has a specific attribute.
        
        Args:
            attribute_value: The attribute value to check
            
        Returns:
            True if the building has the attribute, False otherwise
        """
        attributes = self.get_attributes()
        return attribute_value in attributes
        
    def add_attribute(self, attribute_value: str) -> None:
        """
        Add an attribute to the building's metadata.
        
        Args:
            attribute_value: The attribute value to add
        """
        if self.metadata_ is None:
            self.metadata_ = {}
            
        if 'attributes' not in self.metadata_:
            self.metadata_['attributes'] = []
            
        if attribute_value not in self.metadata_['attributes']:
            self.metadata_['attributes'].append(attribute_value)
            
    def remove_attribute(self, attribute_value: str) -> None:
        """
        Remove an attribute from the building's metadata.
        
        Args:
            attribute_value: The attribute value to remove
        """
        if not self.metadata_ or 'attributes' not in self.metadata_:
            return
            
        if attribute_value in self.metadata_['attributes']:
            self.metadata_['attributes'].remove(attribute_value)
            
    def get_primary_category(self) -> Optional[str]:
        """
        Get the primary category of the building.
        
        Returns:
            The primary category string or None if not set
        """
        if not self.metadata_ or 'category' not in self.metadata_:
            return None
        return self.metadata_['category']
        
    def set_primary_category(self, category: str) -> None:
        """
        Set the primary category of the building.
        
        Args:
            category: The category string to set
        """
        if self.metadata_ is None:
            self.metadata_ = {}
            
        self.metadata_['category'] = category
        self.add_attribute(category)  # Ensure category is also in attributes
        
    def calculate_trait_affinity(self, trait: str) -> float:
        """
        Calculate affinity score between building attributes and a character trait.
        
        Args:
            trait: The character trait string
            
        Returns:
            Float between 0.0 and 1.0 representing affinity score
        """
        # Import here to avoid circular imports
        from app.game_state.enums.building_attributes import calculate_trait_affinity
        
        building_attributes = self.get_attributes()
        return calculate_trait_affinity(building_attributes, trait)

# --- END OF FILE app/game_state/entities/building_blueprint.py ---