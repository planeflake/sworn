from pydantic import Field
from typing import Optional, List
from uuid import UUID

from app.game_state.entities.core.base_pydantic import BaseEntityPydantic


class ActionCategoryPydantic(BaseEntityPydantic):
    """
    Represents a hierarchical category for organizing action templates.
    Examples: "Gathering" -> "Woodcutting", "Crafting" -> "Blacksmithing"
    """
    parent_category_id: Optional[UUID] = None
    description: str = ""
    icon: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    
    # Navigation helpers
    child_categories: List["ActionCategoryPydantic"] = Field(default_factory=list)
    
    def is_root_category(self) -> bool:
        """Check if this is a top-level category."""
        return self.parent_category_id is None
    
    def get_full_path(self, separator: str = " > ") -> str:
        """Get the full category path for display."""
        if self.parent_category_id:
            # In a real implementation, this would traverse up the hierarchy
            return f"Parent{separator}{self.name}"
        return self.name