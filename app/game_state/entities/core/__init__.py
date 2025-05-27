"""Core entities module.

This module contains the base entities and core functionality
that are used by all other entity modules.
"""

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

# Convenience aliases
Theme = ThemeEntity