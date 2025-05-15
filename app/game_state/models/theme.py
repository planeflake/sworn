"""
DEPRECATED: This model is being phased out in favor of using app.game_state.entities.theme.Theme directly.
Use app.game_state.entities.theme.Theme for new code.
"""
import warnings
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

warnings.warn(
    "ThemeEntity is deprecated, use app.game_state.entities.theme.Theme instead",
    DeprecationWarning,
    stacklevel=2
)

@dataclass
class ThemeEntity:
    """
    DEPRECATED: Use app.game_state.entities.theme.Theme instead.
    This class is maintained for backward compatibility during transition.
    """
    id: UUID = uuid4()
    name: str = "Default World"
    description: str = "Default Description"
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        warnings.warn(
            "ThemeEntity is deprecated, use app.game_state.entities.theme.Theme instead",
            DeprecationWarning,
            stacklevel=2
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name, 
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThemeEntity':
        """Create from dictionary"""
        return cls(
            id=data.get("id", uuid4()),
            name=data.get("name", "Default World"), 
            description=data.get("description", "Default Description"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )