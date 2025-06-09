"""
DEPRECATED: This model is being phased out in favor of using Pydantic entities directly.
Use app.game_state.entities.core.theme_pydantic.ThemeEntityPydantic for new code.
"""
import warnings
from typing import Dict, Any
from uuid import UUID, uuid4

# Import the new Pydantic ThemeEntity to re-export
from app.game_state.entities.core.theme_pydantic import ThemeEntityPydantic as RealThemeEntity

warnings.warn(
    "app.game_state.models.theme is deprecated, use app.game_state.entities.core.theme_pydantic.ThemeEntityPydantic instead",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility, re-export ThemeEntity
ThemeEntity = RealThemeEntity

# Add any additional backward compatibility code if needed