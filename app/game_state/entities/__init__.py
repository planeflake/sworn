"""
Entities module for the game state.

This module contains all the domain entities used in the game state.
Each entity is a representation of a game concept and should be treated
as an immutable data structure.
"""

# Core entities
from app.game_state.entities.core.base import BaseEntity
from app.game_state.entities.core.base_pydantic import BaseEntityPydantic
from app.game_state.entities.core.theme import ThemeEntity
from app.game_state.entities.core.theme_pydantic import ThemeEntityPydantic
from app.game_state.entities.core.pydantic_bridge import (
    dataclass_to_pydantic,
    pydantic_to_dataclass,
    is_pydantic,
    is_dataclass,
    ENTITY_TYPE_MAPPING,
    PYDANTIC_TYPE_MAPPING
)

# World entities
from app.game_state.entities.world.world import WorldEntity
from app.game_state.entities.world.world_pydantic import WorldEntityPydantic

# Geography entities
from app.game_state.entities.geography.zone import Zone, ZoneEntity
from app.game_state.entities.geography.zone_pydantic import ZonePydantic
from app.game_state.entities.geography.biome import BiomeEntity
from app.game_state.entities.geography.biome_pydantic import BiomeEntityPydantic
from app.game_state.entities.geography.settlement import SettlementEntity
from app.game_state.entities.geography.settlement_pydantic import SettlementEntityPydantic

# Character entities
from app.game_state.entities.character.character import CharacterEntity
from app.game_state.entities.character.character_pydantic import CharacterEntityPydantic
from app.game_state.entities.character.stat import StatEntity
from app.game_state.entities.character.stat_pydantic import StatEntityPydantic
from app.game_state.entities.character.equipment import EquipmentEntity
from app.game_state.entities.character.equipment_pydantic import EquipmentEntityPydantic
from app.game_state.entities.character.item import ItemEntity, Item
from app.game_state.entities.character.item_pydantic import ItemEntityPydantic

# Building entities
from app.game_state.entities.building.building import BuildingEntity, Building
from app.game_state.entities.building.building_pydantic import BuildingEntityPydantic
from app.game_state.entities.building.building_blueprint import (
    BuildingBlueprintEntity,
    BlueprintStageEntity,
    BlueprintStageFeatureEntity
)
from app.game_state.entities.building.building_blueprint_pydantic import (
    BuildingBlueprintPydantic,
    BlueprintStagePydantic,
    BlueprintStageFeaturePydantic
)
from app.game_state.entities.building.building_instance import BuildingInstanceEntity, BuildingInstance
from app.game_state.entities.building.building_instance_pydantic import BuildingInstanceEntityPydantic
from app.game_state.entities.building.building_upgrade_blueprint import BuildingUpgradeBlueprintEntity
from app.game_state.entities.building.building_upgrade_blueprint_pydantic import BuildingUpgradeBlueprintEntityPydantic

# Skill entities
from app.game_state.entities.skill.skill import SkillEntity
from app.game_state.entities.skill.skill_pydantic import SkillEntityPydantic
from app.game_state.entities.skill.skill_definition import SkillDefinitionEntity
from app.game_state.entities.skill.skill_definition_pydantic import SkillDefinitionEntityPydantic
from app.game_state.entities.skill.profession_definition import ProfessionDefinitionEntity
from app.game_state.entities.skill.profession_definition_pydantic import ProfessionDefinitionEntityPydantic

# Resource entities
from app.game_state.entities.resource.resource import ResourceEntity
from app.game_state.entities.resource.resource_pydantic import ResourceEntityPydantic
from app.game_state.entities.resource.resource_blueprint import ResourceBlueprintEntity
from app.game_state.entities.resource.resource_blueprint_pydantic import ResourceBlueprintEntityPydantic
from app.game_state.entities.resource.resource_node import ResourceNodeEntity, ResourceNodeResourceEntity
from app.game_state.entities.resource.resource_node_pydantic import ResourceNodeEntityPydantic, ResourceNodeResourceEntityPydantic

# Economy entities
from app.game_state.entities.economy.currency import CurrencyEntity, Currency
from app.game_state.entities.economy.currency_pydantic import CurrencyEntityPydantic

# Convenience mappings for common type aliases
World = WorldEntity
Theme = ThemeEntity 
Biome = BiomeEntity
Settlement = SettlementEntity
Character = CharacterEntity
Skill = SkillEntity
SkillDefinition = SkillDefinitionEntity
ProfessionDefinition = ProfessionDefinitionEntity
Resource = ResourceEntity
Stat = StatEntity
Equipment = EquipmentEntity