"""
Bridge module to facilitate the transition from dataclasses to pydantic models.
This module allows services and managers to access both old and new entity types
through a consistent interface while the migration is in progress.
"""

# Import the old dataclass entities
from app.game_state.entities.core.base import BaseEntity
from app.game_state.entities.core.theme import ThemeEntity

# World entities
from app.game_state.entities.world.world import WorldEntity

# Geography entities
from app.game_state.entities.geography.zone import Zone as ZoneEntity
from app.game_state.entities.geography.biome import BiomeEntity
from app.game_state.entities.geography.settlement import SettlementEntity

# Character entities
from app.game_state.entities.character.character import CharacterEntity
from app.game_state.entities.character.stat import StatEntity
from app.game_state.entities.character.equipment import EquipmentEntity
from app.game_state.entities.character.item import ItemEntity

# Building entities
from app.game_state.entities.building.building import BuildingEntity
from app.game_state.entities.building.building_blueprint import (
    BuildingBlueprintEntity, 
    BlueprintStageEntity, 
    BlueprintStageFeatureEntity
)
from app.game_state.entities.building.building_instance import BuildingInstanceEntity
from app.game_state.entities.building.building_upgrade_blueprint import BuildingUpgradeBlueprintEntity

# Skill entities
from app.game_state.entities.skill.skill import SkillEntity
from app.game_state.entities.skill.skill_definition import SkillDefinitionEntity
from app.game_state.entities.skill.profession_definition import ProfessionDefinitionEntity

# Resource entities
from app.game_state.entities.resource.resource import ResourceEntity
try:
    from app.game_state.entities.resource.resource_blueprint import ResourceBlueprintEntity
    from app.game_state.entities.resource.resource_node import ResourceNodeEntity, ResourceNodeResourceEntity
except ImportError:
    # Handle case where these might not be available
    ResourceBlueprintEntity = None
    ResourceNodeEntity = None
    ResourceNodeResourceEntity = None

# Economy entities
from app.game_state.entities.economy.currency import CurrencyEntity

# Import the new pydantic entities
from app.game_state.entities.core.base_pydantic import BaseEntityPydantic
from app.game_state.entities.core.theme_pydantic import ThemeEntityPydantic

# World entities
from app.game_state.entities.world.world_pydantic import WorldEntityPydantic

# Geography entities
from app.game_state.entities.geography.zone_pydantic import ZonePydantic
from app.game_state.entities.geography.biome_pydantic import BiomeEntityPydantic
from app.game_state.entities.geography.settlement_pydantic import SettlementEntityPydantic

# Character entities
from app.game_state.entities.character.character_pydantic import CharacterEntityPydantic
from app.game_state.entities.character.stat_pydantic import StatEntityPydantic
from app.game_state.entities.character.equipment_pydantic import EquipmentEntityPydantic
from app.game_state.entities.character.item_pydantic import ItemEntityPydantic

# Building entities
from app.game_state.entities.building.building_pydantic import BuildingEntityPydantic
from app.game_state.entities.building.building_blueprint_pydantic import (
    BuildingBlueprintPydantic,
    BlueprintStagePydantic,
    BlueprintStageFeaturePydantic
)
from app.game_state.entities.building.building_instance_pydantic import BuildingInstanceEntityPydantic
from app.game_state.entities.building.building_upgrade_blueprint_pydantic import BuildingUpgradeBlueprintEntityPydantic

# Skill entities
from app.game_state.entities.skill.skill_pydantic import SkillEntityPydantic
from app.game_state.entities.skill.skill_definition_pydantic import SkillDefinitionEntityPydantic
from app.game_state.entities.skill.profession_definition_pydantic import ProfessionDefinitionEntityPydantic

# Resource entities
from app.game_state.entities.resource.resource_pydantic import ResourceEntityPydantic
try:
    from app.game_state.entities.resource.resource_blueprint_pydantic import ResourceBlueprintEntityPydantic
    from app.game_state.entities.resource.resource_node_pydantic import ResourceNodeEntityPydantic, ResourceNodeResourceEntityPydantic
except ImportError:
    # Handle case where these might not be available
    ResourceBlueprintEntityPydantic = None
    ResourceNodeEntityPydantic = None
    ResourceNodeResourceEntityPydantic = None

# Economy entities
from app.game_state.entities.economy.currency_pydantic import CurrencyEntityPydantic

# Conversion functions between old and new formats
def dataclass_to_pydantic(entity, pydantic_class):
    """Convert a dataclass entity to its pydantic equivalent."""
    # Use to_dict() to get a serializable form and then construct the pydantic model
    if entity is None:
        return None
    data = entity.to_dict()
    return pydantic_class(**data)

def pydantic_to_dataclass(entity, dataclass_factory):
    """Convert a pydantic entity to its dataclass equivalent."""
    if entity is None:
        return None
    data = entity.model_dump()
    return dataclass_factory(**data)

# Function to check if an entity is pydantic
def is_pydantic(entity):
    """Check if an entity is a pydantic model."""
    return isinstance(entity, BaseEntityPydantic)

# Function to check if an entity is a dataclass
def is_dataclass(entity):
    """Check if an entity is a dataclass."""
    return isinstance(entity, BaseEntity)

# Mapping of old entity types to their pydantic counterparts
ENTITY_TYPE_MAPPING = {
    BaseEntity: BaseEntityPydantic,
    ThemeEntity: ThemeEntityPydantic,
    CharacterEntity: CharacterEntityPydantic,
    BuildingBlueprintEntity: BuildingBlueprintPydantic,
    BlueprintStageEntity: BlueprintStagePydantic,
    BlueprintStageFeatureEntity: BlueprintStageFeaturePydantic,
    BiomeEntity: BiomeEntityPydantic,
    BuildingEntity: BuildingEntityPydantic,
    BuildingInstanceEntity: BuildingInstanceEntityPydantic,
    BuildingUpgradeBlueprintEntity: BuildingUpgradeBlueprintEntityPydantic,
    CurrencyEntity: CurrencyEntityPydantic,
    EquipmentEntity: EquipmentEntityPydantic,
    ItemEntity: ItemEntityPydantic,
    ProfessionDefinitionEntity: ProfessionDefinitionEntityPydantic,
    ResourceEntity: ResourceEntityPydantic,
    SettlementEntity: SettlementEntityPydantic,
    SkillEntity: SkillEntityPydantic,
    SkillDefinitionEntity: SkillDefinitionEntityPydantic,
    StatEntity: StatEntityPydantic,
    WorldEntity: WorldEntityPydantic,
    ZoneEntity: ZonePydantic,
}

# Add resource-related mappings if available
if ResourceBlueprintEntity and ResourceBlueprintEntityPydantic:
    ENTITY_TYPE_MAPPING[ResourceBlueprintEntity] = ResourceBlueprintEntityPydantic
if ResourceNodeEntity and ResourceNodeEntityPydantic:
    ENTITY_TYPE_MAPPING[ResourceNodeEntity] = ResourceNodeEntityPydantic
if ResourceNodeResourceEntity and ResourceNodeResourceEntityPydantic:
    ENTITY_TYPE_MAPPING[ResourceNodeResourceEntity] = ResourceNodeResourceEntityPydantic

# Mapping of pydantic entity types to their dataclass counterparts
PYDANTIC_TYPE_MAPPING = {v: k for k, v in ENTITY_TYPE_MAPPING.items()}