"""World entities module.

This module contains entities related to game worlds.
"""

# Primary Pydantic entities (RECOMMENDED)
from app.game_state.entities.world.world_pydantic import WorldEntityPydantic

# Legacy dataclass entities (for backward compatibility)
try:
    from app.game_state.entities.world.world import WorldEntity
except ImportError:
    # Graceful degradation if legacy entities are removed
    WorldEntity = WorldEntityPydantic

# Convenience aliases pointing to Pydantic entities (RECOMMENDED)
World = WorldEntityPydantic