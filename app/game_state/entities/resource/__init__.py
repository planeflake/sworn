"""Resource entities module.

This module contains entities related to resources,
including resource blueprints and resource nodes.
"""

from app.game_state.entities.resource.resource import ResourceEntity
from app.game_state.entities.resource.resource_pydantic import ResourceEntityPydantic
from app.game_state.entities.resource.resource_blueprint import ResourceBlueprintEntity
from app.game_state.entities.resource.resource_blueprint_pydantic import ResourceBlueprintEntityPydantic
from app.game_state.entities.resource.resource_node import ResourceNodeEntity, ResourceNodeResourceEntity
from app.game_state.entities.resource.resource_node_pydantic import ResourceNodeEntityPydantic, ResourceNodeResourceEntityPydantic

# Convenience aliases
Resource = ResourceEntity
ResourceBlueprint = ResourceBlueprintEntity
ResourceNode = ResourceNodeEntity
ResourceNodeResource = ResourceNodeResourceEntity