"""Resource entities module.

This module contains entities related to resources,
including resource blueprints and resource nodes.
"""

# Primary Pydantic entities (RECOMMENDED)
from app.game_state.entities.resource.resource_pydantic import ResourceEntityPydantic
from app.game_state.entities.resource.resource_blueprint_pydantic import ResourceBlueprintEntityPydantic
from app.game_state.entities.resource.resource_node_pydantic import ResourceNodeEntityPydantic, ResourceNodeResourceEntityPydantic

# Legacy dataclass entities (for backward compatibility)
try:
    from app.game_state.entities.resource.resource import ResourceEntity
    from app.game_state.entities.resource.resource_blueprint import ResourceBlueprintEntity
    from app.game_state.entities.resource.resource_node import ResourceNodeEntity, ResourceNodeResourceEntity
except ImportError:
    # Graceful degradation if legacy entities are removed
    ResourceEntity = ResourceEntityPydantic
    ResourceBlueprintEntity = ResourceBlueprintEntityPydantic
    ResourceNodeEntity = ResourceNodeEntityPydantic
    ResourceNodeResourceEntity = ResourceNodeResourceEntityPydantic

# Convenience aliases pointing to Pydantic entities (RECOMMENDED)
Resource = ResourceEntityPydantic
ResourceBlueprint = ResourceBlueprintEntityPydantic
ResourceNode = ResourceNodeEntityPydantic
ResourceNodeResource = ResourceNodeResourceEntityPydantic