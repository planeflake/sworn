
from app.game_state.managers.skill_definition_manager import SkillDefinitionManager
from app.game_state.repositories.skill_definition_repository import SkillDefinitionRepository
from app.api.schemas.skill import SkillCreate
from app.game_state.entities.skill_definition_entity import SkillDefinitionEntity
from fastapi import HTTPException

class SkillService:
    def __init__(self, db):
        self.db = db
        self.manager = SkillDefinitionManager
        self.repository = SkillDefinitionRepository(db=db)

    async def get_skill(self, skill_id) -> SkillDefinitionEntity:

        skill_exists = await self.repository.find_by_id(skill_id)

        if not skill_exists:
            raise HTTPException(status_code=404, detail="Skill not found")

        skill = await self.repository.find_by_id(skill_id)

        return skill

    async def add_skill(self, skill_data:SkillCreate) -> SkillDefinitionEntity:

        transient_skill:SkillDefinitionEntity = self.manager.create(
            name=skill_data.name,
            max_level=skill_data.max_level,
            description=skill_data.description,
            themes=skill_data.themes,
            metadata=skill_data.metadata
        )

        persistent_skill = await self.repository.save(transient_skill)
        if not persistent_skill:
            raise HTTPException(status_code=500, detail="Failed to save skill")

        return persistent_skill

    async def delete_skill(self, skill_id) -> bool:
        deleted = await self.repository.delete(skill_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Skill not found")
        return deleted

    async def rename_skill(self, skill_id, new_name) -> SkillDefinitionEntity:
        skill = await self.repository.find_by_id(skill_id)
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        skill.name = new_name
        updated_skill = await self.repository.save(skill)
        if not updated_skill:
            raise HTTPException(status_code=500, detail="Failed to update skill")
        return updated_skill