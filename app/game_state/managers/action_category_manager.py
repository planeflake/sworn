import uuid
from typing import Optional
from datetime import datetime

from app.game_state.entities.action.action_category_pydantic import ActionCategoryPydantic
from .base_manager import BaseManager


class ActionCategoryManager(BaseManager[ActionCategoryPydantic]):
    """Manager for action category business logic and creation."""
    
    @staticmethod
    def create_category(
        name: str,
        parent_category_id: Optional[uuid.UUID] = None,
        description: str = "",
        icon: Optional[str] = None,
        display_order: int = 0,
        entity_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> ActionCategoryPydantic:
        """Create a new action category."""
        create_params = {
            "name": name,
            "parent_category_id": parent_category_id,
            "description": description,
            "icon": icon,
            "display_order": display_order,
            "is_active": True,
            **kwargs
        }
        
        if entity_id:
            create_params["entity_id"] = entity_id
            
        return ActionCategoryManager.create(ActionCategoryPydantic, **create_params)
    
    @staticmethod
    def create_root_category(
        name: str,
        description: str = "",
        icon: Optional[str] = None,
        display_order: int = 0,
        **kwargs
    ) -> ActionCategoryPydantic:
        """Create a new root-level category (no parent)."""
        return ActionCategoryManager.create_category(
            name=name,
            parent_category_id=None,
            description=description,
            icon=icon,
            display_order=display_order,
            **kwargs
        )
    
    @staticmethod
    def create_subcategory(
        name: str,
        parent_id: uuid.UUID,
        description: str = "",
        icon: Optional[str] = None,
        display_order: int = 0,
        **kwargs
    ) -> ActionCategoryPydantic:
        """Create a new subcategory under an existing parent."""
        return ActionCategoryManager.create_category(
            name=name,
            parent_category_id=parent_id,
            description=description,
            icon=icon,
            display_order=display_order,
            **kwargs
        )