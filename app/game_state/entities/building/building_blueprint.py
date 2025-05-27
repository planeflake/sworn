# --- START OF FILE app/game_state/entities/building_blueprint.py ---

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import uuid4

from ..base import BaseEntity  # Assuming app.game_state.entities.base.BaseEntity

class BlueprintStageFeatureEntity(BaseEntity):
    """Domain Entity for an optional feature within a blueprint stage."""

    def __init__(
            self,
            blueprint_stage_id: uuid.UUID,
            feature_key: str,
            description: Optional[str] = None,
            required_professions: Optional[List[uuid.UUID]] = None,
            additional_resource_costs: Optional[List[Dict[str, Any]]] = None,
            additional_duration_days: Optional[float] = None,
            effects: Optional[Dict[str, Any]] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
            entity_id: Optional[uuid.UUID] = None,
            name: str = "Unnamed Feature"
    ):
        # Initialize base class
        super().__init__(entity_id=entity_id or uuid4(), name=name)

        # Initialize required fields
        self.blueprint_stage_id = blueprint_stage_id
        self.feature_key = feature_key

        # Initialize optional fields
        self.description = description
        self.required_professions = required_professions or []
        self.additional_resource_costs = additional_resource_costs or []
        self.additional_duration_days = additional_duration_days
        self.effects = effects or {}
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    @classmethod
    def from_db(cls, db_feature) -> 'BlueprintStageFeatureEntity':
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

    # Add to_dict method to maintain dataclass-like behavior
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        })
        return result


# No dataclass decorator
class BlueprintStageEntity(BaseEntity):
    """Domain Entity for a stage within a building blueprint."""

    def __init__(
            self,
            building_blueprint_id: uuid.UUID,
            stage_number: int,
            description: Optional[str] = None,
            duration_days: float = 0.0,
            resource_costs: Optional[List[Dict[str, Any]]] = None,
            profession_time_bonus: Optional[List[Dict[str, Any]]] = None,
            stage_completion_bonuses: Optional[List[Dict[str, Any]]] = None,
            optional_features: Optional[List[BlueprintStageFeatureEntity]] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
            entity_id: Optional[uuid.UUID] = None,
            name: str = "Unnamed Stage"
    ):
        # Initialize base class
        super().__init__(entity_id=entity_id or uuid4(), name=name)

        # Initialize required fields
        self.building_blueprint_id = building_blueprint_id
        self.stage_number = stage_number

        # Initialize optional fields
        self.description = description
        self.duration_days = duration_days
        self.resource_costs = resource_costs or []
        self.profession_time_bonus = profession_time_bonus or []
        self.stage_completion_bonuses = stage_completion_bonuses or []
        self.optional_features = optional_features or []
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    @classmethod
    async def from_db(cls, db_stage, convert_features: bool = True) -> 'BlueprintStageEntity':
        """Create a new entity from a database model instance."""
        stage_entity = cls(
            entity_id=db_stage.id,
            name=db_stage.name,
            building_blueprint_id=db_stage.building_blueprint_id,
            stage_number=db_stage.stage_number,
            description=db_stage.description,
            duration_days=getattr(db_stage, 'duration_days', 0.0),
            resource_costs=getattr(db_stage, 'resource_costs', []),
            profession_time_bonus=getattr(db_stage, 'profession_time_bonus', []),
            stage_completion_bonuses=getattr(db_stage, 'stage_completion_bonuses', []),
            optional_features=[],  # Initialize empty, add later if needed
            created_at=getattr(db_stage, 'created_at', None),
            updated_at=getattr(db_stage, 'updated_at', None)
        )

        # Handle optional features if requested and they exist
        if convert_features and hasattr(db_stage, 'optional_features') and db_stage.optional_features:
            features = []
            for db_feature in db_stage.optional_features:
                features.append(BlueprintStageFeatureEntity.from_db(db_feature))
            stage_entity.optional_features = features

        return stage_entity

    # Add to_dict method to maintain dataclass-like behavior
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        })
        return result


# No dataclass decorator
class BuildingBlueprintEntity(BaseEntity):
    """Domain Entity for a building blueprint definition."""

    def __init__(
            self,
            theme_id: uuid.UUID,
            description: Optional[str] = None,
            is_unique_per_settlement: bool = False,
            metadata_: Optional[Dict[str, Any]] = None,
            stages: Optional[List[BlueprintStageEntity]] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
            entity_id: Optional[uuid.UUID] = None,
            name: str = "Unnamed Blueprint"
    ):
        # Initialize base class
        super().__init__(entity_id=entity_id or uuid4(), name=name)

        # Initialize required fields
        self.theme_id = theme_id

        # Initialize optional fields
        self.description = description
        self.is_unique_per_settlement = is_unique_per_settlement
        self.metadata_ = metadata_ or {}
        self.stages = stages or []
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

        # Run post-init logic
        self.__post_init__()

    @classmethod
    async def from_db(cls, db_obj, convert_stages: bool = True) -> Optional['BuildingBlueprintEntity']:
        """Create a new entity from a database model instance."""
        if db_obj is None:
            return None

        # Create the entity with base fields
        blueprint_entity = cls(
            entity_id=db_obj.id,
            name=db_obj.name,
            theme_id=db_obj.theme_id,
            description=db_obj.description,
            is_unique_per_settlement=getattr(db_obj, 'is_unique_per_settlement', False),
            metadata_=getattr(db_obj, '_metadata', {}),
            stages=[],  # Initialize empty, add later if needed
            created_at=getattr(db_obj, 'created_at', None),
            updated_at=getattr(db_obj, 'updated_at', None)
        )

        # Handle stages if requested and they exist
        if convert_stages and hasattr(db_obj, 'stages') and db_obj.stages:
            stages = []
            for db_stage in db_obj.stages:
                stages.append(await BlueprintStageEntity.from_db(db_stage))
            blueprint_entity.stages = stages

        return blueprint_entity

    def __post_init__(self):
        # Sort stages by stage_number if they are provided out of order
        if self.stages:
            self.stages.sort(key=lambda s: s.stage_number)

        # Initialize metadata if needed
        if self.metadata_ is None:
            self.metadata_ = {}

        # Ensure attributes list exists in metadata
        if 'attributes' not in self.metadata_:
            self.metadata_['attributes'] = []

    # Add to_dict method to maintain dataclass-like behavior
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            'theme_id': str(self.theme_id),
            'description': self.description,
            'is_unique_per_settlement': self.is_unique_per_settlement,
            'metadata_': self.metadata_,
            'stages': [s.to_dict() for s in self.stages],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
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

# --- END OF FILE app/game_state/entities/building_blueprint.py ---