"""
Entities module for the game state.

This module contains all the domain entities used in the game state.
All entities use Pydantic for validation and serialization.
"""

# Core entities (Pydantic-based)
from app.game_state.entities.core.base_pydantic import BaseEntityPydantic
from app.game_state.entities.core.theme_pydantic import ThemeEntityPydantic
from app.game_state.entities.core.tool_tier_pydantic import ToolTierPydantic

# World entities (Pydantic-based)
from app.game_state.entities.world.world_pydantic import WorldEntityPydantic

# Geography entities (Pydantic-based)
from app.game_state.entities.geography.zone_pydantic import ZonePydantic
from app.game_state.entities.geography.biome_pydantic import BiomeEntityPydantic
from app.game_state.entities.geography.settlement_pydantic import SettlementEntityPydantic
from app.game_state.entities.geography.area_pydantic import AreaEntityPydantic
from app.game_state.entities.geography.location_pydantic import LocationEntityPydantic
from app.game_state.entities.geography.location_type_pydantic import LocationTypeEntityPydantic

# Character entities (Pydantic-based)
from app.game_state.entities.character.character_pydantic import CharacterEntityPydantic
from app.game_state.entities.character.stat_pydantic import StatEntityPydantic
from app.game_state.entities.character.equipment_pydantic import EquipmentEntityPydantic
from app.game_state.entities.character.item_pydantic import ItemEntityPydantic

# Building entities (Pydantic-based)
from app.game_state.entities.building.building_pydantic import BuildingEntityPydantic
from app.game_state.entities.building.building_blueprint_pydantic import (
    BuildingBlueprintPydantic,
    BlueprintStagePydantic,
    BlueprintStageFeaturePydantic
)
from app.game_state.entities.building.building_instance_pydantic import BuildingInstanceEntityPydantic
from app.game_state.entities.building.building_upgrade_blueprint_pydantic import BuildingUpgradeBlueprintEntityPydantic

# Skill entities (Pydantic-based)
from app.game_state.entities.skill.skill_pydantic import SkillEntityPydantic
from app.game_state.entities.skill.skill_definition_pydantic import SkillDefinitionEntityPydantic
from app.game_state.entities.skill.profession_definition_pydantic import ProfessionDefinitionEntityPydantic

# Resource entities (Pydantic-based)
from app.game_state.entities.resource.resource_pydantic import ResourceEntityPydantic
from app.game_state.entities.resource.resource_blueprint_pydantic import ResourceBlueprintEntityPydantic
from app.game_state.entities.resource.resource_node_pydantic import (
    ResourceNodeEntityPydantic,
    ResourceNodeResourceEntityPydantic
)

# Economy entities (Pydantic-based)
from app.game_state.entities.economy.currency_pydantic import CurrencyEntityPydantic

# Action entities (Pydantic-based)
from app.game_state.entities.action.action_category_pydantic import ActionCategoryPydantic
from app.game_state.entities.action.action_template_pydantic import ActionTemplatePydantic
from app.game_state.entities.action.character_action_pydantic import CharacterActionPydantic

# Legacy dataclass entities (DEPRECATED - use Pydantic versions above)
# These are kept for backward compatibility only
try:
    from app.game_state.entities.core.base import BaseEntity
    from app.game_state.entities.core.theme import ThemeEntity
    from app.game_state.entities.world.world import WorldEntity
    from app.game_state.entities.geography.zone import Zone, ZoneEntity
    from app.game_state.entities.geography.biome import BiomeEntity
    from app.game_state.entities.geography.settlement import SettlementEntity
    from app.game_state.entities.character.character import CharacterEntity
    from app.game_state.entities.character.stat import StatEntity
    from app.game_state.entities.character.equipment import EquipmentEntity
    from app.game_state.entities.character.item import ItemEntity, Item
    from app.game_state.entities.building.building import BuildingEntity, Building
    from app.game_state.entities.building.building_blueprint import (
        BuildingBlueprintEntity,
        BlueprintStageEntity,
        BlueprintStageFeatureEntity
    )
    from app.game_state.entities.building.building_instance import BuildingInstanceEntity, BuildingInstance
    from app.game_state.entities.building.building_upgrade_blueprint import BuildingUpgradeBlueprintEntity
    from app.game_state.entities.skill.skill import SkillEntity
    from app.game_state.entities.skill.skill_definition import SkillDefinitionEntity
    from app.game_state.entities.skill.profession_definition import ProfessionDefinitionEntity
    from app.game_state.entities.resource.resource import ResourceEntity
    from app.game_state.entities.resource.resource_blueprint import ResourceBlueprintEntity
    from app.game_state.entities.resource.resource_node import ResourceNodeEntity, ResourceNodeResourceEntity
    from app.game_state.entities.economy.currency import CurrencyEntity, Currency
except ImportError:
    # Legacy dataclass entities removed
    pass

# Pydantic bridge for converting between dataclass and Pydantic entities
try:
    from app.game_state.entities.core.pydantic_bridge import (
        dataclass_to_pydantic,
        pydantic_to_dataclass,
        is_pydantic,
        is_dataclass,
        ENTITY_TYPE_MAPPING,
        PYDANTIC_TYPE_MAPPING
    )
except ImportError:
    # Pydantic bridge removed
    pass

# Convenience aliases pointing to Pydantic entities (RECOMMENDED)
World = WorldEntityPydantic
Theme = ThemeEntityPydantic
Biome = BiomeEntityPydantic
Zone = ZonePydantic
Settlement = SettlementEntityPydantic
Location = LocationEntityPydantic
LocationType = LocationTypeEntityPydantic
Character = CharacterEntityPydantic
Skill = SkillEntityPydantic
SkillDefinition = SkillDefinitionEntityPydantic
ProfessionDefinition = ProfessionDefinitionEntityPydantic
Resource = ResourceEntityPydantic
ResourceBlueprint = ResourceBlueprintEntityPydantic
ResourceNode = ResourceNodeEntityPydantic
Stat = StatEntityPydantic
Equipment = EquipmentEntityPydantic
Item = ItemEntityPydantic
Building = BuildingEntityPydantic
BuildingBlueprint = BuildingBlueprintPydantic
BuildingInstance = BuildingInstanceEntityPydantic
BuildingUpgradeBlueprint = BuildingUpgradeBlueprintEntityPydantic
Currency = CurrencyEntityPydantic
ToolTier = ToolTierPydantic
ActionCategory = ActionCategoryPydantic
ActionTemplate = ActionTemplatePydantic
CharacterAction = CharacterActionPydantic