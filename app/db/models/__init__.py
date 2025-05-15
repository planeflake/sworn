# app/db/models/__init__.py
from .base import Base  # Import the Base

# Import each model class or module
from .world import World
from .theme import Theme
from .settlement import Settlement
from .character import Character
from .resource import Resource
from .season import Season
from .building_blueprint import BuildingBlueprint
from .blueprint_stage import BlueprintStage
from .blueprint_stage_feature import BlueprintStageFeature
from .building_instance import BuildingInstanceDB  # Renamed to avoid clash with domain entity
#from .stage_resource_cost import StageResourceCost
#from .stage_profession_cost import StageProfessionCost
from .profession_definition import ProfessionDefinition
from .item import Item
from .skill import Skill
from .location import Location
from .skill_definition import SkillDefinition
from .building_upgrade_blueprint import BuildingUpgradeBlueprint
from .building_instance import BuildingInstanceDB
from .biome import Biome