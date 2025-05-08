# --- START OF FILE app/game_state/managers/profession_manager.py ---

from app.game_state.entities.profession_definition_entity import ProfessionDefinitionEntity
from app.game_state.managers.base_manager import BaseManager # Import the BaseManager
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid as uuid_module # Keep for clarity if needed elsewhere

class ProfessionManager:
    """Manager class for profession definition domain logic. Uses BaseManager for creation."""

    @staticmethod
    def create(
        name: str, # BaseEntity requires name, pass it explicitly
        display_name: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        skill_requirements: Optional[List[Dict[str, Any]]] = None,
        available_theme_ids: Optional[List[UUID]] = None,
        valid_unlock_methods: Optional[List[str]] = None,
        unlock_condition_details: Optional[List[Dict[str, Any]]] = None,
        python_class_override: Optional[str] = None,
        archetype_handler: Optional[str] = None,
        configuration_data: Optional[Dict[str, Any]] = None,
        # Change 'id' parameter name to 'entity_id' to match BaseManager/BaseEntity convention
        entity_id: Optional[UUID] = None
    ) -> ProfessionDefinitionEntity:
        """
        Creates a new transient (in-memory) ProfessionDefinitionEntity using BaseManager.
        """

        # Prepare keyword arguments for the entity constructor,
        # handling None values by defaulting to empty collections/dicts where appropriate.
        entity_kwargs = {
            "display_name": display_name,
            "description": description,
            "category": category,
            "skill_requirements": skill_requirements if skill_requirements is not None else [],
            "available_theme_ids": available_theme_ids if available_theme_ids is not None else [],
            "valid_unlock_methods": valid_unlock_methods if valid_unlock_methods is not None else [],
            "unlock_condition_details": unlock_condition_details if unlock_condition_details is not None else [],
            "python_class_override": python_class_override,
            "archetype_handler": archetype_handler,
            "configuration_data": configuration_data if configuration_data is not None else {},
            "name": name # Pass the name explicitly as BaseEntity needs it
        }

        # Remove keys with None values if the dataclass __init__ doesn't handle them gracefully
        # or if you only want explicitly provided values passed. Dataclasses usually handle None fine.
        # entity_kwargs = {k: v for k, v in entity_kwargs.items() if v is not None}
        # entity_kwargs["name"] = name # Ensure name is always passed

        # Call BaseManager.create, passing the specific entity class and kwargs
        # Note: Pass entity_id as 'id' to match BaseManager's parameter name.
        # BaseManager will generate a UUID if entity_id is None.
        profession_entity = BaseManager.create(
            entity_class=ProfessionDefinitionEntity,
            id=entity_id, # Pass entity_id to BaseManager's 'id' parameter
            **entity_kwargs
        )

        # BaseManager returns the created entity instance
        return profession_entity

# --- END OF FILE app/game_state/managers/profession_manager.py ---