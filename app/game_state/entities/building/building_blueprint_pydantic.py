from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import Field, field_validator, ConfigDict

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic

class BlueprintStageFeaturePydantic(BaseEntityPydantic):
    """Domain Entity for an optional feature within a blueprint stage."""
    
    blueprint_stage_id: UUID
    feature_key: str
    description: Optional[str] = None
    required_professions: List[UUID] = Field(default_factory=list)
    additional_resource_costs: List[Dict[str, Any]] = Field(default_factory=list)
    additional_duration_days: Optional[float] = None
    effects: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def from_db(cls, db_feature) -> 'BlueprintStageFeaturePydantic':
        """Create a new entity from a database model instance."""
        return cls(
            entity_id=db_feature.id,
            name=db_feature.name,
            blueprint_stage_id=db_feature.blueprint_stage_id,
            feature_key=db_feature.feature_key,
            description=db_feature.description,
            required_professions=getattr(db_feature, 'required_professions', []),
            additional_resource_costs=getattr(db_feature, 'additional_resource_costs', []),
            additional_duration_days=getattr(db_feature, 'additional_duration_days', None),
            effects=getattr(db_feature, 'effects', {}),
            created_at=getattr(db_feature, 'created_at', None),
            updated_at=getattr(db_feature, 'updated_at', None)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            'blueprint_stage_id': str(self.blueprint_stage_id),
            'feature_key': self.feature_key,
            'description': self.description,
            'required_professions': [str(p) for p in self.required_professions],
            'additional_resource_costs': self.additional_resource_costs,
            'additional_duration_days': self.additional_duration_days,
            'effects': self.effects,
        })
        return result
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


class BlueprintStagePydantic(BaseEntityPydantic):
    """Domain Entity for a stage within a building blueprint."""
    
    building_blueprint_id: UUID
    stage_number: int
    description: Optional[str] = None
    duration_days: float = 0.0
    resource_costs: List[Dict[str, Any]] = Field(default_factory=list)
    profession_time_bonus: List[Dict[str, Any]] = Field(default_factory=list)
    stage_completion_bonuses: List[Dict[str, Any]] = Field(default_factory=list)
    optional_features: List[BlueprintStageFeaturePydantic] = Field(default_factory=list)
    
    @classmethod
    async def from_db(cls, db_stage, convert_features: bool = True) -> 'BlueprintStagePydantic':
        """Create a new entity from a database model instance."""
        stage_data = {
            'entity_id': db_stage.id,
            'name': db_stage.name,
            'building_blueprint_id': db_stage.building_blueprint_id,
            'stage_number': db_stage.stage_number,
            'description': db_stage.description,
            'duration_days': getattr(db_stage, 'duration_days', 0.0),
            'resource_costs': getattr(db_stage, 'resource_costs', []),
            'profession_time_bonus': getattr(db_stage, 'profession_time_bonus', []),
            'stage_completion_bonuses': getattr(db_stage, 'stage_completion_bonuses', []),
            'optional_features': [],  # Initialize empty, add later if needed
            'created_at': getattr(db_stage, 'created_at', None),
            'updated_at': getattr(db_stage, 'updated_at', None)
        }
        
        stage_entity = cls(**stage_data)

        # Handle optional features if requested and they exist
        if convert_features and hasattr(db_stage, 'optional_features') and db_stage.optional_features:
            features = []
            for db_feature in db_stage.optional_features:
                features.append(BlueprintStageFeaturePydantic.from_db(db_feature))
            stage_entity.optional_features = features

        return stage_entity
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            'building_blueprint_id': str(self.building_blueprint_id),
            'stage_number': self.stage_number,
            'description': self.description,
            'duration_days': self.duration_days,
            'resource_costs': self.resource_costs,
            'profession_time_bonus': self.profession_time_bonus,
            'stage_completion_bonuses': self.stage_completion_bonuses,
            'optional_features': [f.to_dict() for f in self.optional_features],
        })
        return result
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


class BuildingBlueprintPydantic(BaseEntityPydantic):
    """Domain Entity for a building blueprint definition."""
    
    theme_id: UUID
    description: Optional[str] = None
    is_unique_per_settlement: bool = False
    metadata_: Dict[str, Any] = Field(default_factory=dict)
    stages: List[BlueprintStagePydantic] = Field(default_factory=list)
    
    @field_validator('metadata_')
    @classmethod
    def validate_metadata(cls, v):
        """Ensure metadata has required structure."""
        if v is None:
            v = {}
        if 'attributes' not in v:
            v['attributes'] = []
        return v

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            'theme_id': str(self.theme_id),
            'description': self.description,
            'is_unique_per_settlement': self.is_unique_per_settlement,
            'metadata_': self.metadata_,
            'stages': [s.to_dict() for s in self.stages],
        })
        return result
    
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
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )