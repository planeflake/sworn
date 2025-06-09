# --- START OF FILE app/game_state/managers/skill_definition_manager.py ---

from app.game_state.entities.skill.skill_definition_pydantic import SkillDefinitionEntityPydantic
from app.game_state.managers.base_manager import BaseManager
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid as uuid_module

class SkillDefinitionManager:
    """Manager class for Skill Definition domain logic."""

    @staticmethod
    def create(
        name: str, # User-facing name, required by BaseEntity
        # skill_key: str, # If using a separate unique key
        max_level: int = 100,
        description: Optional[str] = None,
        themes: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        entity_id: Optional[UUID] = None
    ) -> SkillDefinitionEntityPydantic:
        """
        Creates a new transient (in-memory) SkillDefinitionEntity using BaseManager.
        """
        entity_kwargs = {
            "name": name, # Maps to BaseEntity's name
            "description": description,
            "max_level": max_level,
            "themes": themes if themes is not None else [],
            "metadata": metadata if metadata is not None else {},
            # "skill_key": skill_key, # If using skill_key
        }

        skill_def_entity = BaseManager.create(
            entity_class=SkillDefinitionEntityPydantic,
            entity_id=entity_id, # Pass to BaseManager
            **entity_kwargs
        )

        return skill_def_entity

# --- END OF FILE app/game_state/managers/skill_definition_manager.py ---