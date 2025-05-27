"""Skill entities module.

This module contains entities related to skills and professions.
"""

from app.game_state.entities.skill.skill import SkillEntity
from app.game_state.entities.skill.skill_pydantic import SkillEntityPydantic
from app.game_state.entities.skill.skill_definition import SkillDefinitionEntity
from app.game_state.entities.skill.skill_definition_pydantic import SkillDefinitionEntityPydantic
from app.game_state.entities.skill.profession_definition import ProfessionDefinitionEntity
from app.game_state.entities.skill.profession_definition_pydantic import ProfessionDefinitionEntityPydantic

# Convenience aliases
Skill = SkillEntity
SkillDefinition = SkillDefinitionEntity
ProfessionDefinition = ProfessionDefinitionEntity