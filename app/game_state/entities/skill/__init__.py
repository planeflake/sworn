"""Skill entities module.

This module contains entities related to skills and professions.
"""

# Primary Pydantic entities (RECOMMENDED)
from app.game_state.entities.skill.skill_pydantic import SkillEntityPydantic
from app.game_state.entities.skill.skill_definition_pydantic import SkillDefinitionEntityPydantic
from app.game_state.entities.skill.profession_definition_pydantic import ProfessionDefinitionEntityPydantic

# Legacy dataclass entities (for backward compatibility)
try:
    from app.game_state.entities.skill.skill import SkillEntity
    from app.game_state.entities.skill.skill_definition import SkillDefinitionEntity
    from app.game_state.entities.skill.profession_definition import ProfessionDefinitionEntity
except ImportError:
    # Graceful degradation if legacy entities are removed
    SkillEntity = SkillEntityPydantic
    SkillDefinitionEntity = SkillDefinitionEntityPydantic
    ProfessionDefinitionEntity = ProfessionDefinitionEntityPydantic

# Convenience aliases pointing to Pydantic entities (RECOMMENDED)
Skill = SkillEntityPydantic
SkillDefinition = SkillDefinitionEntityPydantic
ProfessionDefinition = ProfessionDefinitionEntityPydantic