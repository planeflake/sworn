# app/db/models/__init__.py
from .base import Base  # Import the Base

# Import each model class or module
from .world import World
from .theme import ThemeDB
from .settlement import Settlement
from .character import Character
from app.db.models.resources.resource_blueprint import ResourceBlueprint
from app.db.models.resources.resource_node_blueprint import ResourceNodeBlueprint
from app.db.models.resources.resource_node_blueprint_link import ResourceNodeBlueprintResource
from app.db.models.resources.resource_instance import ResourceInstance
from app.db.models.resources.resource_node import ResourceNode
from app.db.models.resources.resource_node_link import ResourceNodeLink
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
# Import location models in the correct order to resolve dependencies
from .location_type import LocationType  # Location type definitions come first
from .location_instance import LocationInstance  # New model to replace Location and LocationEntity
from .travel_link import TravelLink
from .wildlife import Wildlife
from .character_faction_relationship import CharacterFactionRelationship
from .skill_definition import SkillDefinition
from .building_upgrade_blueprint import BuildingUpgradeBlueprint
from .celestial_events import CelestialEventDB
from .biome import Biome
# The following models are DEPRECATED and will be replaced by LocationInstance:
from .zone import Zone  # DEPRECATED - Use LocationInstance with appropriate location_type
from .settlement import Settlement  # DEPRECATED - Use LocationInstance with appropriate location_type
from .faction import Faction