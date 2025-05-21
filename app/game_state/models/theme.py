"""
DEPRECATED: This model is being phased out in favor of using app.game_state.entities.theme.ThemeEntity directly.
Use app.game_state.entities.theme.ThemeEntity for new code.
"""
import warnings
from typing import Dict, Any
from uuid import UUID, uuid4

# Import the real ThemeEntity to re-export
from app.game_state.entities.theme import ThemeEntity as RealThemeEntity

warnings.warn(
    "app.game_state.models.theme is deprecated, use app.game_state.entities.theme.ThemeEntity instead",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility, re-export ThemeEntity
ThemeEntity = RealThemeEntity

# Add any additional backward compatibility code if needed